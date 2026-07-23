import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Alert,
  App,
  Button,
  DatePicker,
  Divider,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Table,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { BookOutlined, DeleteOutlined, PrinterOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  checkCompatibility,
  createPrescription,
  generatePrescriptionHtml,
  listInventory,
  listMedicines,
} from '@/api/tauri';
import EmptyState from '@/components/EmptyState';
import TemplateSelector from '@/components/TemplateSelector';
import { printHtmlInIframe } from '@/utils/print';
import { formatError } from '@/utils/formatError';
import type { Medicine, PrescriptionItem } from '@/types';
import type { PrescriptionTemplate } from '@/services/templateService';

const { Title, Paragraph, Text } = Typography;

interface PatientForm {
  patient_name: string;
  patient_age?: number;
  patient_gender: string;
  diagnosis: string;
  created_by: string;
}

export default function PrescriptionPage() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [form] = Form.useForm<PatientForm>();

  const [keyword, setKeyword] = useState('');
  const [items, setItems] = useState<PrescriptionItem[]>([]);
  const [createdDate, setCreatedDate] = useState<dayjs.Dayjs>(dayjs());
  const [lastCreatedId, setLastCreatedId] = useState<number | null>(null);
  const [printing, setPrinting] = useState(false);
  const [templateOpen, setTemplateOpen] = useState(false);

  // 药材搜索
  const { data: medicines } = useQuery({
    queryKey: ['medicines', keyword, undefined],
    queryFn: () => listMedicines(keyword || undefined, undefined),
  });

  // 库存（用于取价格/单位与库存校验）
  const { data: inventory } = useQuery({
    queryKey: ['inventory'],
    queryFn: listInventory,
  });

  // 库存按药材聚合（一药多批后取总量与首批次价格/单位）
  const inventoryMap = useMemo(() => {
    const map = new Map<number, { totalQty: number; price: number; unit: string }>();
    inventory?.forEach((i) => {
      const cur = map.get(i.medicine_id);
      if (cur) {
        cur.totalQty += i.quantity;
      } else {
        map.set(i.medicine_id, { totalQty: i.quantity, price: i.price, unit: i.unit });
      }
    });
    return map;
  }, [inventory]);

  // 配伍禁忌检查（至少两味药才检查）
  const names = useMemo(() => items.map((i) => i.medicine_name), [items]);
  const { data: conflicts } = useQuery({
    queryKey: ['compatibility', names.join('|')],
    queryFn: () => checkCompatibility(names),
    enabled: names.length >= 2,
  });

  const totalAmount = useMemo(
    () => items.reduce((sum, i) => sum + i.amount, 0),
    [items],
  );

  const createMutation = useMutation({
    mutationFn: createPrescription,
    onSuccess: (id) => {
      message.success(`处方已保存（编号 ${id}）`);
      queryClient.invalidateQueries({ queryKey: ['prescriptions'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      setLastCreatedId(id);
      // 重置
      form.resetFields();
      setItems([]);
      setCreatedDate(dayjs());
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  const handlePrint = async (id: number) => {
    setPrinting(true);
    try {
      const html = await generatePrescriptionHtml(id);
      printHtmlInIframe(html);
      message.success('已发送至打印预览');
    } catch (e) {
      message.error(formatError(e));
    } finally {
      setPrinting(false);
    }
  };

  const addMedicine = (m: Medicine) => {
    if (!m.id) return;
    const mid = m.id;
    if (items.some((i) => i.medicine_id === mid)) {
      message.warning(`${m.name} 已在处方中`);
      return;
    }
    const inv = inventoryMap.get(mid);
    const price = inv?.price ?? 0;
    const unit = inv?.unit ?? 'g';
    const quantity = 10;
    setItems((prev) => [
      ...prev,
      {
        medicine_id: mid,
        medicine_name: m.name,
        quantity,
        unit,
        price,
        amount: Number((quantity * price).toFixed(2)),
      },
    ]);
  };

  // 应用方剂模板：自动填入诊断并按模板组成匹配药材加入处方
  const applyTemplate = async (template: PrescriptionTemplate) => {
    // 1. 自动设置诊断字段为模板主治
    form.setFieldValue('diagnosis', template.indication);

    const found: { medicine: Medicine; quantity: number }[] = [];
    const missing: string[] = [];

    // 2. 一次拉取全部药材，内存中按名称匹配（消除 N 次 invoke 调用）
    const allMedicines = await listMedicines(undefined, undefined);
    const medicineMap = new Map(allMedicines.map((m) => [m.name, m]));
    for (const tpl of template.items) {
      const matched = medicineMap.get(tpl.name);
      if (matched && matched.id !== null) {
        found.push({ medicine: matched, quantity: tpl.quantity });
      } else {
        missing.push(tpl.name);
      }
    }

    // 3. 找到的药材添加到处方列表（跳过已存在，单价/单位取自库存）
    setItems((prev) => {
      const existingIds = new Set(prev.map((i) => i.medicine_id));
      const additions: PrescriptionItem[] = [];
      for (const { medicine, quantity } of found) {
        if (!medicine.id || existingIds.has(medicine.id)) continue;
        const mid = medicine.id;
        const inv = inventoryMap.get(mid);
        const price = inv?.price ?? 0;
        const unit = inv?.unit ?? 'g';
        additions.push({
          medicine_id: mid,
          medicine_name: medicine.name,
          quantity,
          unit,
          price,
          amount: Number((quantity * price).toFixed(2)),
        });
        existingIds.add(mid);
      }
      return [...prev, ...additions];
    });

    // 4. 未找到的药材提示
    if (missing.length > 0) {
      message.warning(`以下药材未找到：${missing.join('、')}`);
    }
    if (found.length > 0) {
      message.success(`已加载方剂「${template.name}」共 ${found.length} 味药材`);
    }
  };

  const updateItem = (index: number, field: 'quantity' | 'price', value: number) => {
    setItems((prev) =>
      prev.map((it, i) => {
        if (i !== index) return it;
        const next = { ...it, [field]: value };
        next.amount = Number((next.quantity * next.price).toFixed(2));
        return next;
      }),
    );
  };

  const removeItem = (index: number) => {
    setItems((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (items.length === 0) {
      message.warning('请至少添加一味药材');
      return;
    }
    // 库存预校验：检查每味药跨批次总库存是否足够（FEFO 会跨批次扣减）
    const insufficient = items
      .map((i) => {
        const stock = inventoryMap.get(i.medicine_id);
        const totalQty = stock?.totalQty ?? 0;
        return totalQty < i.quantity ? `${i.medicine_name}(需${i.quantity}${i.unit}，库存${totalQty}${i.unit})` : null;
      })
      .filter((s): s is string => s !== null);
    if (insufficient.length > 0) {
      message.error(`库存不足：${insufficient.join('、')}`);
      return;
    }
    try {
      const values = await form.validateFields();
      createMutation.mutate({
        id: null,
        patient_name: values.patient_name ?? '',
        patient_age: values.patient_age ?? null,
        patient_gender: values.patient_gender ?? '',
        diagnosis: values.diagnosis ?? '',
        total_amount: Number(totalAmount.toFixed(2)),
        created_by: values.created_by ?? '',
        created_at: createdDate.format('YYYY-MM-DD HH:mm:ss'),
        items: items.map((i) => ({ ...i, amount: Number(i.amount.toFixed(2)) })),
      });
    } catch {
      // 表单校验失败
    }
  };

  const itemColumns: ColumnsType<PrescriptionItem> = [
    { title: '药材', dataIndex: 'medicine_name', key: 'medicine_name', width: 120 },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 120,
      render: (q: number, _r, index) => (
        <InputNumber
          min={0}
          step={1}
          value={q}
          onChange={(v) => updateItem(index, 'quantity', Number(v ?? 0))}
        />
      ),
    },
    { title: '单位', dataIndex: 'unit', key: 'unit', width: 70 },
    {
      title: '单价',
      dataIndex: 'price',
      key: 'price',
      width: 110,
      render: (p: number, _r, index) => (
        <InputNumber
          min={0}
          step={0.01}
          value={p}
          onChange={(v) => updateItem(index, 'price', Number(v ?? 0))}
        />
      ),
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
      align: 'right',
      render: (a: number) => `¥${a.toFixed(2)}`,
    },
    {
      title: '',
      key: 'action',
      width: 60,
      render: (_v, _r, index) => (
        <Button
          type="link"
          danger
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => removeItem(index)}
        />
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={4} style={{ marginBottom: 4 }}>
          开处方
        </Title>
        <Paragraph type="secondary" style={{ margin: 0 }}>
          左侧检索药材加入处方，系统自动校验十八反/十九畏配伍禁忌并扣减库存
        </Paragraph>
      </div>

      {conflicts && conflicts.length > 0 && (
        <Alert
          className="compat-alert"
          type="error"
          showIcon
          message="配伍禁忌预警"
          description={
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {conflicts.map((c, i) => (
                <li key={i}>{c.description}</li>
              ))}
            </ul>
          }
        />
      )}

      <div className="prescription-layout">
        {/* 左侧：药材检索 */}
        <div className="prescription-search-panel">
          <Button
            icon={<BookOutlined />}
            block
            onClick={() => setTemplateOpen(true)}
            style={{ marginBottom: 8 }}
          >
            方剂模板
          </Button>
          <Input.Search
            placeholder="搜索药材"
            allowClear
            onSearch={setKeyword}
            style={{ marginBottom: 8 }}
          />
          <div>
            {medicines && medicines.length > 0 ? (
              medicines.map((m) => (
                <div
                  key={m.id}
                  className="medicine-search-item"
                  onClick={() => addMedicine(m)}
                >
                  <div className="name">{m.name}</div>
                  <div className="meta">
                    {m.category ? `${m.category} · ` : ''}
                    {[m.nature, m.taste].filter(Boolean).join(' ') || '—'}
                  </div>
                </div>
              ))
            ) : (
              <EmptyState title="暂无药材，请搜索" />
            )}
          </div>
        </div>

        {/* 右侧：处方编辑 */}
        <div className="prescription-edit-panel">
          <Form form={form} layout="vertical">
            <Space style={{ display: 'flex', width: '100%' }} size="middle" wrap>
              <Form.Item
                name="patient_name"
                label="患者姓名"
                rules={[{ required: true, message: '请输入患者姓名' }]}
                style={{ flex: 1, minWidth: 140 }}
              >
                <Input placeholder="如：张三" />
              </Form.Item>
              <Form.Item name="patient_age" label="年龄" style={{ width: 100 }}>
                <InputNumber min={0} max={150} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="patient_gender" label="性别" style={{ width: 120 }}>
                <Select
                  placeholder="选择性别"
                  options={[
                    { label: '男', value: '男' },
                    { label: '女', value: '女' },
                  ]}
                />
              </Form.Item>
              <Form.Item name="created_by" label="开方人" style={{ width: 140 }}>
                <Input placeholder="如：李医生" />
              </Form.Item>
              <Form.Item label="开方日期" style={{ width: 180 }}>
                <DatePicker
                  showTime
                  value={createdDate}
                  onChange={(v) => v && setCreatedDate(v)}
                />
              </Form.Item>
            </Space>
            <Form.Item name="diagnosis" label="诊断">
              <Input.TextArea autoSize={{ minRows: 1 }} placeholder="诊断与证候" />
            </Form.Item>
          </Form>

          <Divider style={{ margin: '8px 0 12px' }} />

          <Table<PrescriptionItem>
            rowKey={(r) => `${r.medicine_id}`}
            size="small"
            columns={itemColumns}
            dataSource={items}
            pagination={false}
            locale={{ emptyText: <EmptyState title="请添加药材到处方" /> }}
            footer={() => (
              <div style={{ textAlign: 'right', fontWeight: 600 }}>
                合计：<Text type="danger">¥{totalAmount.toFixed(2)}</Text>
              </div>
            )}
          />

          <div style={{ marginTop: 16, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => { form.resetFields(); setItems([]); }}>
                清空
              </Button>
              <Button
                type="primary"
                loading={createMutation.isPending}
                onClick={handleSubmit}
              >
                保存处方
              </Button>
              {lastCreatedId !== null && (
                <Button
                  icon={<PrinterOutlined />}
                  loading={printing}
                  onClick={() => handlePrint(lastCreatedId)}
                >
                  打印刚才的处方
                </Button>
              )}
            </Space>
          </div>
        </div>
      </div>

      <TemplateSelector
        open={templateOpen}
        onClose={() => setTemplateOpen(false)}
        onSelect={applyTemplate}
      />
    </div>
  );
}
