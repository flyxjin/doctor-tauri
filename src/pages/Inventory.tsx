import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Alert,
  App,
  Button,
  Card,
  Col,
  DatePicker,
  Drawer,
  Form,
  Input,
  InputNumber,
  Modal,
  Radio,
  Row,
  Segmented,
  Space,
  Statistic,
  Table,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import {
  AlertOutlined,
  ClockCircleOutlined,
  DatabaseOutlined,
  ExclamationCircleOutlined,
  ExportOutlined,
  HistoryOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import {
  listExpiringBatches,
  listInventory,
  listInventoryHistory,
  saveTextToDownloads,
  updateStock,
} from '@/api/tauri';
import { formatError } from '@/utils/formatError';
import type { Inventory, InventoryHistory } from '@/types';

const { Text } = Typography;

interface StockForm {
  change: number;
  is_in: boolean;
  operator?: string;
  notes?: string;
  batch_no?: string;
  production_date?: Dayjs | null;
  expiry_date?: Dayjs | null;
}

type FilterMode = 'all' | 'low' | 'zero' | 'expiring';

/** 距效期多少天开始标黄预警 */
const EXPIRY_WARN_DAYS = 30;

/** 判断批次效期状态：expired=已过期，near=近效期，ok=正常，none=无期 */
function expiryStatus(dateStr?: string | null): 'expired' | 'near' | 'ok' | 'none' {
  if (!dateStr) return 'none';
  const d = dayjs(dateStr);
  if (!d.isValid()) return 'none';
  const today = dayjs().startOf('day');
  if (d.isBefore(today)) return 'expired';
  if (d.isBefore(today.add(EXPIRY_WARN_DAYS, 'day'))) return 'near';
  return 'ok';
}

export default function InventoryPage() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [form] = Form.useForm<StockForm>();
  const [modalOpen, setModalOpen] = useState(false);
  const [target, setTarget] = useState<Inventory | null>(null);
  const [filterMode, setFilterMode] = useState<FilterMode>('all');
  const [keyword, setKeyword] = useState('');
  const [historyTarget, setHistoryTarget] = useState<Inventory | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: listInventory,
  });

  // 效期预警批次（30 天内到期或已过期）
  const { data: expiringData } = useQuery({
    queryKey: ['expiring-batches', EXPIRY_WARN_DAYS],
    queryFn: () => listExpiringBatches(EXPIRY_WARN_DAYS),
  });

  // 库存变更历史（仅当选择某药材时查询）
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['inventory-history', historyTarget?.medicine_id],
    queryFn: () => listInventoryHistory(historyTarget!.medicine_id, undefined, undefined, undefined, 100),
    enabled: !!historyTarget,
  });

  // 按药材聚合的汇总（一药多批后统计口径需跨批次合并）
  const medicineSummary = useMemo(() => {
    const list = data ?? [];
    const map = new Map<number, { totalQty: number; minStock: number; name: string; category: string }>();
    for (const i of list) {
      const cur = map.get(i.medicine_id);
      if (cur) {
        cur.totalQty += i.quantity;
        cur.minStock = Math.min(cur.minStock, i.min_stock);
      } else {
        map.set(i.medicine_id, {
          totalQty: i.quantity,
          minStock: i.min_stock,
          name: i.medicine_name ?? '',
          category: i.category ?? '',
        });
      }
    }
    return map;
  }, [data]);

  // 统计：总品种数（按药材去重）、低库存数、零库存数、总价值
  const stats = useMemo(() => {
    const list = data ?? [];
    const totalValue = list.reduce((sum, i) => sum + i.quantity * i.price, 0);
    let lowCount = 0;
    let zeroCount = 0;
    for (const [, s] of medicineSummary) {
      if (s.totalQty <= 0) zeroCount++;
      else if (s.totalQty <= s.minStock) lowCount++;
    }
    return { totalKinds: medicineSummary.size, lowCount, zeroCount, totalValue };
  }, [data, medicineSummary]);

  // 近效期批次数（用于筛选标签计数）
  const expiringCount = useMemo(() => {
    return (data ?? []).filter((i) => {
      const st = expiryStatus(i.expiry_date);
      return st === 'expired' || st === 'near';
    }).length;
  }, [data]);

  // 筛选：按模式 + 关键字
  const filteredData = useMemo(() => {
    let list = data ?? [];
    if (filterMode === 'low') {
      // 低库存：按药材聚合后总量 <= min_stock
      const lowIds = new Set<number>();
      for (const [id, s] of medicineSummary) {
        if (s.totalQty > 0 && s.totalQty <= s.minStock) lowIds.add(id);
      }
      list = list.filter((i) => lowIds.has(i.medicine_id));
    } else if (filterMode === 'zero') {
      // 零库存：按药材聚合后总量 <= 0
      const zeroIds = new Set<number>();
      for (const [id, s] of medicineSummary) {
        if (s.totalQty <= 0) zeroIds.add(id);
      }
      list = list.filter((i) => zeroIds.has(i.medicine_id));
    } else if (filterMode === 'expiring') {
      // 近效期：批次已过期或 30 天内到期
      list = list.filter((i) => {
        const st = expiryStatus(i.expiry_date);
        return st === 'expired' || st === 'near';
      });
    }
    if (keyword.trim()) {
      const k = keyword.trim().toLowerCase();
      list = list.filter(
        (i) =>
          i.medicine_name?.toLowerCase().includes(k) ||
          i.category?.toLowerCase().includes(k) ||
          i.batch_no?.toLowerCase().includes(k),
      );
    }
    return list;
  }, [data, filterMode, keyword, medicineSummary]);

  const mutation = useMutation({
    mutationFn: (vars: { medicineId: number; form: StockForm }) =>
      updateStock(
        vars.medicineId,
        vars.form.change,
        vars.form.is_in,
        vars.form.operator,
        vars.form.notes,
        vars.form.batch_no,
        vars.form.production_date?.format('YYYY-MM-DD'),
        vars.form.expiry_date?.format('YYYY-MM-DD'),
      ),
    onSuccess: (_d, vars) => {
      message.success(`${vars.form.is_in ? '入库' : '出库'}成功`);
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['expiring-batches', EXPIRY_WARN_DAYS] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setModalOpen(false);
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  const openModal = (record: Inventory, isIn: boolean) => {
    setTarget(record);
    form.resetFields();
    form.setFieldsValue({
      change: 0,
      is_in: isIn,
      operator: '',
      notes: '',
      batch_no: '',
      production_date: null,
      expiry_date: null,
    });
    setModalOpen(true);
  };

  // 导出当前筛选后的库存为 CSV（含 BOM 以兼容 Excel）
  const handleExportCsv = async () => {
    const list = filteredData;
    if (list.length === 0) {
      message.warning('没有可导出的数据');
      return;
    }
    const header = [
      '药材',
      '分类',
      '批次号',
      '生产日期',
      '效期',
      '库存量',
      '单位',
      '最低库存',
      '单价',
      '批次价值',
      '备注',
    ];
    const escape = (v: string | number | null | undefined) => {
      const s = v == null ? '' : String(v);
      // 含逗号/引号/换行的字段用双引号包裹并转义内部引号
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const lines = [header.join(',')];
    for (const i of list) {
      lines.push(
        [
          escape(i.medicine_name),
          escape(i.category),
          escape(i.batch_no),
          escape(i.production_date),
          escape(i.expiry_date),
          i.quantity,
          escape(i.unit),
          i.min_stock,
          i.price.toFixed(2),
          (i.quantity * i.price).toFixed(2),
          escape(i.notes),
        ].join(','),
      );
    }
    const csv = '\uFEFF' + lines.join('\n');
    try {
      const ts = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      const path = await saveTextToDownloads(`inventory_export_${ts}.csv`, csv);
      message.success(`已导出到：${path}`);
    } catch (e) {
      message.error(formatError(e));
    }
  };

  // 订阅 is_in 字段变化，使 Modal 标题与批次输入区随操作类型切换
  const isInWatch = Form.useWatch('is_in', form);

  const handleSubmit = async () => {
    if (!target) return;
    try {
      const values = await form.validateFields();
      if (values.change <= 0) {
        message.warning('数量必须大于 0');
        return;
      }
      // 出库预校验：检查该药材跨批次总库存（FEFO 会跨批次扣减）
      if (!values.is_in) {
        const summary = medicineSummary.get(target.medicine_id);
        const totalQty = summary?.totalQty ?? 0;
        if (values.change > totalQty) {
          message.warning(`库存不足，当前总库存 ${totalQty} ${target.unit || 'g'}`);
          return;
        }
      }
      mutation.mutate({ medicineId: target.medicine_id, form: values });
    } catch {
      // 校验失败
    }
  };

  const columns: ColumnsType<Inventory> = [
    { title: '药材', dataIndex: 'medicine_name', key: 'medicine_name', width: 130, fixed: 'left' },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 90,
      render: (c: string) => (c ? <Tag color="blue">{c}</Tag> : '-'),
    },
    {
      title: '批次号',
      dataIndex: 'batch_no',
      key: 'batch_no',
      width: 130,
      render: (b: string) => b || <Text type="secondary">—</Text>,
    },
    {
      title: '效期',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      width: 130,
      render: (d: string | null) => {
        const st = expiryStatus(d);
        if (st === 'none') return <Text type="secondary">—</Text>;
        if (st === 'expired') {
          return (
            <Tooltip title="已过期，请尽快处理">
              <Tag color="red" icon={<ExclamationCircleOutlined />}>{d}</Tag>
            </Tooltip>
          );
        }
        if (st === 'near') {
          return (
            <Tooltip title={`${EXPIRY_WARN_DAYS} 天内到期`}>
              <Tag color="orange" icon={<ClockCircleOutlined />}>{d}</Tag>
            </Tooltip>
          );
        }
        return <Text>{d}</Text>;
      },
    },
    {
      title: '库存量',
      key: 'quantity',
      width: 110,
      render: (_v, r) => {
        const low = r.quantity <= r.min_stock;
        return (
          <span style={{ color: low ? '#dc2626' : undefined, fontWeight: low ? 600 : 400 }}>
            {r.quantity} {r.unit}
          </span>
        );
      },
    },
    { title: '最低库存', dataIndex: 'min_stock', key: 'min_stock', width: 100 },
    {
      title: '单价',
      dataIndex: 'price',
      key: 'price',
      width: 90,
      align: 'right',
      render: (p: number) => `¥${p.toFixed(2)}`,
    },
    {
      title: '批次价值',
      key: 'value',
      width: 110,
      align: 'right',
      render: (_v, r) => `¥${(r.quantity * r.price).toFixed(2)}`,
    },
    { title: '备注', dataIndex: 'notes', key: 'notes', ellipsis: true },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_v, record) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => openModal(record, true)}>
            入库
          </Button>
          <Button type="link" size="small" danger onClick={() => openModal(record, false)}>
            出库
          </Button>
          <Button
            type="link"
            size="small"
            icon={<HistoryOutlined />}
            onClick={() => setHistoryTarget(record)}
          >
            历史
          </Button>
        </Space>
      ),
    },
  ];

  // 库存变更历史表格列定义
  const historyColumns: ColumnsType<InventoryHistory> = [
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 90,
      render: (t: string) => {
        const colorMap: Record<string, string> = {
          '入库': 'green',
          '出库': 'orange',
          '退库': 'blue',
        };
        return <Tag color={colorMap[t] ?? 'default'}>{t}</Tag>;
      },
    },
    { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 90, align: 'right' },
    {
      title: '单价',
      dataIndex: 'price',
      key: 'price',
      width: 90,
      align: 'right',
      render: (p: number | null) => (p != null ? `¥${p.toFixed(2)}` : '-'),
    },
    {
      title: '金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 100,
      align: 'right',
      render: (a: number | null) => (a != null ? `¥${a.toFixed(2)}` : '-'),
    },
    { title: '操作人', dataIndex: 'operator', key: 'operator', width: 90, ellipsis: true },
    { title: '备注', dataIndex: 'notes', key: 'notes', ellipsis: true },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (t: string) => t ?? '-',
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">库存管理</h1>
        <p className="page-subtitle">
          按批次管理库存，入库录入批次号与效期，出库按近效期优先（FEFO）自动扣减
        </p>
      </div>

      {/* 效期预警横幅 */}
      {expiringData && expiringData.length > 0 && (
        <Alert
          type="warning"
          showIcon
          icon={<ClockCircleOutlined />}
          style={{ marginBottom: 16 }}
          message={`${expiringData.length} 个批次即将到期或已过期`}
          description={
            <Space size={[8, 4]} wrap>
              {expiringData.slice(0, 5).map((b) => (
                <Tag
                  key={b.id}
                  color={expiryStatus(b.expiry_date) === 'expired' ? 'red' : 'orange'}
                >
                  {b.medicine_name} · {b.batch_no} · {b.expiry_date} · {b.quantity}
                  {b.unit}
                </Tag>
              ))}
              {expiringData.length > 5 && <Text type="secondary">等 {expiringData.length} 项…</Text>}
            </Space>
          }
        />
      )}

      {/* 库存概览统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="在库品种"
              value={stats.totalKinds}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="低库存预警"
              value={stats.lowCount}
              valueStyle={{ color: stats.lowCount > 0 ? '#fa8c16' : undefined }}
              prefix={<ExclamationCircleOutlined />}
              suffix="种"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="零库存"
              value={stats.zeroCount}
              valueStyle={{ color: stats.zeroCount > 0 ? '#cf1322' : undefined }}
              prefix={<AlertOutlined />}
              suffix="种"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="库存总价值"
              value={stats.totalValue}
              precision={2}
              prefix="¥"
              suffix={<SafetyCertificateOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
      </Row>

      <div className="table-card">
        <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Segmented<FilterMode>
              value={filterMode}
              onChange={(v) => setFilterMode(v)}
              options={[
                { label: '全部', value: 'all' },
                { label: `低库存${stats.lowCount > 0 ? ` (${stats.lowCount})` : ''}`, value: 'low' },
                { label: `零库存${stats.zeroCount > 0 ? ` (${stats.zeroCount})` : ''}`, value: 'zero' },
                { label: `近效期${expiringCount > 0 ? ` (${expiringCount})` : ''}`, value: 'expiring' },
              ]}
            />
            <Input.Search
              placeholder="搜索药材名 / 分类 / 批次号"
              allowClear
              style={{ width: 260 }}
              onSearch={setKeyword}
            />
          </Space>
          <Button
            icon={<ExportOutlined />}
            onClick={handleExportCsv}
            disabled={filteredData.length === 0}
          >
            导出 CSV
          </Button>
        </Space>
        <Table<Inventory>
          rowKey="id"
          loading={isLoading}
          columns={columns}
          dataSource={filteredData}
          scroll={{ x: 1300 }}
          pagination={{ pageSize: 15, showSizeChanger: true }}
          rowClassName={(record) => {
            const summary = medicineSummary.get(record.medicine_id);
            const totalQty = summary?.totalQty ?? record.quantity;
            if (totalQty <= 0) return 'row-zero-stock';
            if (totalQty <= record.min_stock) return 'row-low-stock';
            return '';
          }}
          locale={{
            emptyText: `无${
              filterMode === 'low' ? '低库存' : filterMode === 'zero' ? '零库存' : filterMode === 'expiring' ? '近效期' : ''
            }库存记录`,
          }}
        />
      </div>

      <Modal
        title={`${target?.medicine_name ?? ''} - ${isInWatch ? '入库' : '出库'}`}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        confirmLoading={mutation.isPending}
        okText="确认"
        cancelText="取消"
        width={480}
      >
        {target && (
          <Alert
            type={isInWatch ? 'info' : 'warning'}
            showIcon
            style={{ marginBottom: 16 }}
            message={
              <span>
                当前总库存：
                <Text strong style={{ fontSize: 16 }}>
                  {medicineSummary.get(target.medicine_id)?.totalQty ?? target.quantity}{' '}
                  {target.unit}
                </Text>
                {isInWatch ? (
                  <Text type="secondary" style={{ marginLeft: 12 }}>
                    批次余量：{target.quantity} {target.unit}
                  </Text>
                ) : null}
              </span>
            }
          />
        )}
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item name="is_in" label="操作类型">
            <Radio.Group
              onChange={(e) => form.setFieldValue('is_in', e.target.value)}
            >
              <Radio value={true}>入库</Radio>
              <Radio value={false}>出库</Radio>
            </Radio.Group>
          </Form.Item>
          <Form.Item
            name="change"
            label="数量"
            rules={[{ required: true, message: '请输入数量' }]}
          >
            <InputNumber min={0} step={1} style={{ width: '100%' }} />
          </Form.Item>

          {/* 入库时录入批次信息；出库时按 FEFO 自动扣减，无需填写 */}
          {isInWatch && (
            <>
              <Form.Item name="batch_no" label="批次号" tooltip="留空将自动按时间戳生成批次号；同批次号入库会合并数量">
                <Input placeholder="如 BATCH-20260723-01，留空自动生成" />
              </Form.Item>
              <Row gutter={12}>
                <Col span={12}>
                  <Form.Item name="production_date" label="生产日期">
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="expiry_date" label="效期" tooltip="近效期批次出库时优先扣减">
                    <DatePicker style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
            </>
          )}

          {!isInWatch && (
            <Alert
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
              message="出库按近效期优先（FEFO）自动跨批次扣减"
              description="若当前批次库存不足，系统将自动扣减最近效期的下一批次"
            />
          )}

          <Form.Item name="operator" label="操作人">
            <Input placeholder="操作人姓名" />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input.TextArea autoSize={{ minRows: 1 }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 库存变更历史抽屉 */}
      <Drawer
        title={`${historyTarget?.medicine_name ?? ''} - 库存变更历史`}
        open={!!historyTarget}
        onClose={() => setHistoryTarget(null)}
        width={720}
      >
        {historyTarget && (
          <>
            <Space size="large" style={{ marginBottom: 16 }}>
              <Text type="secondary">
                当前库存：
                <Text strong style={{ fontSize: 16 }}>
                  {medicineSummary.get(historyTarget.medicine_id)?.totalQty ?? historyTarget.quantity}{' '}
                  {historyTarget.unit}
                </Text>
              </Text>
              <Text type="secondary">
                单价：
                <Text strong>¥{historyTarget.price.toFixed(2)}</Text>
              </Text>
            </Space>
            <Table<InventoryHistory>
              rowKey="id"
              loading={historyLoading}
              columns={historyColumns}
              dataSource={historyData}
              size="small"
              pagination={{ pageSize: 10, showSizeChanger: true }}
              locale={{
                emptyText: '暂无变更记录',
              }}
            />
          </>
        )}
      </Drawer>
    </div>
  );
}
