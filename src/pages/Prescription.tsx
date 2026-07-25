import { useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Alert,
  App,
  AutoComplete,
  Button,
  DatePicker,
  Divider,
  Form,
  Input,
  InputNumber,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { BookOutlined, DeleteOutlined, PrinterOutlined, WarningOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  checkCompatibility,
  createPrescription,
  generatePrescriptionHtml,
  listInventory,
  listMedicines,
  listPatients,
} from '@/api/tauri';
import EmptyState from '@/components/EmptyState';
import TemplateSelector from '@/components/TemplateSelector';
import { printHtmlInIframe } from '@/utils/print';
import { formatError } from '@/utils/formatError';
import { aggregateInventory } from '@/utils/inventory';
import { checkAllergy } from '@/utils/allergy';
import { parseDefaultDosage } from '@/utils/dosage';
import type { Medicine, Patient, PrescriptionItem } from '@/types';
import type { PrescriptionTemplate } from '@/services/templateService';
import { PRESCRIPTION_COPY_KEY } from '@/constants/prescription';

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
  const { message, modal } = App.useApp();
  const [form] = Form.useForm<PatientForm>();

  const [keyword, setKeyword] = useState('');
  const [items, setItems] = useState<PrescriptionItem[]>([]);
  const [createdDate, setCreatedDate] = useState<dayjs.Dayjs>(dayjs());
  const [lastCreatedId, setLastCreatedId] = useState<number | null>(null);
  const [printing, setPrinting] = useState(false);
  const [templateOpen, setTemplateOpen] = useState(false);
  // 当前选中患者的过敏史（用于开方时过敏预警）
  const [patientAllergy, setPatientAllergy] = useState<string | null>(null);

  // 患者档案列表（用于患者姓名 AutoComplete 与过敏史回填）
  const { data: patients } = useQuery({
    queryKey: ['patients', ''],
    queryFn: () => listPatients(undefined),
    staleTime: 5 * 60 * 1000,
  });

  // 药材搜索
  const { data: medicines } = useQuery({
    queryKey: ['medicines', keyword, undefined],
    queryFn: () => listMedicines(keyword || undefined, undefined),
    staleTime: 5 * 60 * 1000,
  });

  // 库存（用于取价格/单位与库存校验）
  const { data: inventory } = useQuery({
    queryKey: ['inventory'],
    queryFn: listInventory,
    staleTime: 60 * 1000,
  });

  // 库存按药材聚合（一药多批后取总量与首批次价格/单位）
  const inventoryMap = useMemo(() => aggregateInventory(inventory ?? []), [inventory]);

  // 患者姓名 AutoComplete 选项（显示姓名+年龄，选中后回填年龄/性别/过敏史）
  const patientOptions = useMemo(() => {
    return (patients ?? []).map((p) => ({
      value: p.name,
      label: (
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>{p.name}</span>
          <span style={{ color: '#8B8580', fontSize: 12 }}>
            {[p.gender, p.age != null ? `${p.age}岁` : ''].filter(Boolean).join(' · ')}
            {p.allergy ? ' · ⚠过敏' : ''}
          </span>
        </div>
      ),
      patient: p,
    }));
  }, [patients]);

  // 药材库 Map（用于过敏史校验时按 medicine_id 查 contraindication）
  const medicineMap = useMemo(() => {
    const map = new Map<number, Medicine>();
    for (const m of medicines ?? []) {
      if (m.id) map.set(m.id, m);
    }
    return map;
  }, [medicines]);

  // 过敏史冲突检测（患者有过敏史且处方非空时计算）
  const allergyConflicts = useMemo(() => {
    if (!patientAllergy || items.length === 0) return [];
    return checkAllergy(items, medicineMap, patientAllergy);
  }, [items, medicineMap, patientAllergy]);

  // 选中患者后回填年龄/性别/过敏史
  const handlePatientSelect = (value: string, option: { patient?: Patient }) => {
    const p = option.patient;
    if (!p) {
      setPatientAllergy(null);
      return;
    }
    form.setFieldsValue({
      patient_name: value,
      patient_age: p.age ?? undefined,
      patient_gender: p.gender ?? '',
    });
    setPatientAllergy(p.allergy ?? null);
  };

  // 处理复制的处方数据预填
  // - 表单头字段通过 form.setFieldsValue 预填，明细通过 setItems 预填
  // - 开方日期重置为当前时间（新处方）
  // - 重置 lastCreatedId，避免用户误打印上一张已保存处方
  const processCopyData = (raw: string) => {
    try {
      const payload = JSON.parse(raw) as {
        patient_name: string;
        patient_age?: number | null;
        patient_gender?: string;
        diagnosis?: string;
        created_by?: string;
        items: Array<{
          medicine_id: number;
          medicine_name: string;
          quantity: number;
          unit: string;
          price: number;
          amount: number;
        }>;
      };
      form.setFieldsValue({
        patient_name: payload.patient_name,
        patient_age: payload.patient_age ?? undefined,
        patient_gender: payload.patient_gender ?? '',
        diagnosis: payload.diagnosis ?? '',
        created_by: payload.created_by ?? '',
      });
      setItems(
        payload.items.map((i) => ({
          medicine_id: i.medicine_id,
          medicine_name: i.medicine_name,
          quantity: i.quantity,
          unit: i.unit,
          price: i.price,
          amount: Number((i.quantity * i.price).toFixed(2)),
        })),
      );
      setCreatedDate(dayjs());
      setLastCreatedId(null);
      message.success(`已加载原方 ${payload.items.length} 味药材，请核对后保存`);
    } catch {
      message.error('复制的处方数据解析失败，请重试');
    }
  };

  // 挂载时检测 sessionStorage 是否有待复制的处方（来自 History 页「复制到处方」）
  //
  // 设计要点：
  // - 空依赖数组，仅在挂载时执行一次
  // - 读取后立即清除 key，避免刷新页面重复预填
  // - 沿用原方价格（医生可在处方页手动调整，符合复诊实际）
  // - 若当前已有未保存内容，弹窗确认是否覆盖，避免静默丢失用户工作
  useEffect(() => {
    const raw = sessionStorage.getItem(PRESCRIPTION_COPY_KEY);
    if (!raw) return;
    sessionStorage.removeItem(PRESCRIPTION_COPY_KEY);

    const hasUnsavedContent = items.length > 0 || form.getFieldValue('patient_name');
    if (hasUnsavedContent) {
      modal.confirm({
        title: '检测到待复制的处方',
        content: '当前已有未保存的处方内容，是否覆盖？',
        okText: '覆盖',
        cancelText: '取消',
        onOk: () => processCopyData(raw),
      });
    } else {
      processCopyData(raw);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
      setPatientAllergy(null);
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
    // 从药材 dosage 字段解析推荐起始用量（如"3-9g"取 3），无法解析时回退 10
    const quantity = parseDefaultDosage(m.dosage) ?? 10;
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
    // 确保库存数据已加载（复制处方后首次提交时可能尚未完成加载）
    let invData = inventory;
    if (!invData) {
      try {
        message.loading({ content: '库存数据加载中...', key: 'inv-loading' });
        invData = await queryClient.fetchQuery({ queryKey: ['inventory'] });
      } catch {
        message.error('库存数据加载失败，请稍后重试');
        return;
      } finally {
        message.destroy('inv-loading');
      }
    }
    // 构建 inventoryMap（按药材聚合跨批次总库存）
    const invMap = new Map<number, number>();
    invData?.forEach((i) => {
      invMap.set(i.medicine_id, (invMap.get(i.medicine_id) ?? 0) + i.quantity);
    });
    // 库存预校验：检查每味药跨批次总库存是否足够（FEFO 会跨批次扣减）
    const insufficient = items
      .map((i) => {
        const totalQty = invMap.get(i.medicine_id) ?? 0;
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
    {
      title: '药材',
      dataIndex: 'medicine_name',
      key: 'medicine_name',
      width: 140,
      render: (name: string, r) => {
        const stock = inventoryMap.get(r.medicine_id);
        const totalQty = stock?.totalQty ?? 0;
        const insufficient = totalQty < r.quantity;
        return (
          <div>
            <div>{name}</div>
            <div style={{ fontSize: 11, marginTop: 2 }}>
              {totalQty > 0 ? (
                <span style={{ color: insufficient ? '#B83A2E' : '#8B8580' }}>
                  库存 {totalQty}{r.unit}
                  {insufficient && ' · 不足'}
                </span>
              ) : (
                <span style={{ color: '#B83A2E' }}>无库存</span>
              )}
            </div>
          </div>
        );
      },
    },
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

      {/* 患者过敏史提示与冲突预警 */}
      {patientAllergy && allergyConflicts.length === 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          style={{ marginBottom: 12 }}
          message={
            <span>
              患者过敏史：
              <Tag color="red" style={{ marginLeft: 4 }}>
                {patientAllergy}
              </Tag>
              <Text type="secondary" style={{ marginLeft: 8 }}>
                当前处方药材未命中过敏原
              </Text>
            </span>
          }
        />
      )}
      {allergyConflicts.length > 0 && (
        <Alert
          type="error"
          showIcon
          icon={<WarningOutlined />}
          style={{ marginBottom: 12 }}
          message="过敏史冲突预警"
          description={
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {allergyConflicts.map((c, i) => (
                <li key={i}>
                  处方含「{c.medicine_name}」— 患者对「{c.allergen}」过敏
                  {c.matchType === 'contraindication' && '（药材禁忌字段提及）'}
                </li>
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
                <AutoComplete
                  placeholder="输入姓名可选择已有患者"
                  options={patientOptions}
                  filterOption={(input, option) =>
                    String(option?.value ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  onSelect={handlePatientSelect}
                  onChange={(v) => {
                    // 手动输入但未选中患者时，清除过敏史
                    const matched = patients?.find((p) => p.name === v);
                    setPatientAllergy(matched?.allergy ?? null);
                  }}
                />
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
                  onChange={(v) => setCreatedDate(v ?? dayjs())}
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
              <Popconfirm
                title="确认清空当前处方？"
                description="将清空所有药材与表单内容，此操作不可撤销"
                okText="清空"
                cancelText="取消"
                okButtonProps={{ danger: true }}
                onConfirm={() => {
                  form.resetFields();
                  setItems([]);
                  setCreatedDate(dayjs());
                  setLastCreatedId(null);
                  setPatientAllergy(null);
                }}
                disabled={items.length === 0 && !form.getFieldValue('patient_name')}
              >
                <Button
                  disabled={items.length === 0 && !form.getFieldValue('patient_name')}
                >
                  清空
                </Button>
              </Popconfirm>
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
