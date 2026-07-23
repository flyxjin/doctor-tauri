import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  App,
  Button,
  Card,
  Col,
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
  Typography,
} from 'antd';
import {
  AlertOutlined,
  DatabaseOutlined,
  ExclamationCircleOutlined,
  HistoryOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { listInventory, listInventoryHistory, updateStock } from '@/api/tauri';
import { formatError } from '@/utils/formatError';
import type { Inventory, InventoryHistory } from '@/types';

const { Text } = Typography;

interface StockForm {
  change: number;
  is_in: boolean;
  operator?: string;
  notes?: string;
}

type FilterMode = 'all' | 'low' | 'zero';

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

  // 库存变更历史（仅当选择某药材时查询）
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['inventory-history', historyTarget?.medicine_id],
    queryFn: () => listInventoryHistory(historyTarget!.medicine_id, undefined, undefined, undefined, 100),
    enabled: !!historyTarget,
  });

  // 统计：总品种数、低库存数、零库存数、总价值
  const stats = useMemo(() => {
    const list = data ?? [];
    const totalValue = list.reduce((sum, i) => sum + i.quantity * i.price, 0);
    const lowCount = list.filter((i) => i.quantity > 0 && i.quantity <= i.min_stock).length;
    const zeroCount = list.filter((i) => i.quantity <= 0).length;
    return { total: list.length, lowCount, zeroCount, totalValue };
  }, [data]);

  // 筛选：按模式 + 关键字
  const filteredData = useMemo(() => {
    let list = data ?? [];
    if (filterMode === 'low') {
      list = list.filter((i) => i.quantity > 0 && i.quantity <= i.min_stock);
    } else if (filterMode === 'zero') {
      list = list.filter((i) => i.quantity <= 0);
    }
    if (keyword.trim()) {
      const k = keyword.trim().toLowerCase();
      list = list.filter(
        (i) =>
          i.medicine_name?.toLowerCase().includes(k) ||
          i.category?.toLowerCase().includes(k),
      );
    }
    return list;
  }, [data, filterMode, keyword]);

  const mutation = useMutation({
    mutationFn: (vars: { medicineId: number; form: StockForm }) =>
      updateStock(
        vars.medicineId,
        vars.form.change,
        vars.form.is_in,
        vars.form.operator,
        vars.form.notes,
      ),
    onSuccess: (_d, vars) => {
      message.success(`${vars.form.is_in ? '入库' : '出库'}成功`);
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setModalOpen(false);
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  const openModal = (record: Inventory, isIn: boolean) => {
    setTarget(record);
    form.resetFields();
    form.setFieldsValue({ change: 0, is_in: isIn, operator: '', notes: '' });
    setModalOpen(true);
  };

  // 订阅 is_in 字段变化，使 Modal 标题随操作类型切换实时更新
  const isInWatch = Form.useWatch('is_in', form);

  const handleSubmit = async () => {
    if (!target) return;
    try {
      const values = await form.validateFields();
      if (values.change <= 0) {
        message.warning('数量必须大于 0');
        return;
      }
      // 出库预校验：前端先检查库存余量，避免等后端拒绝
      if (!values.is_in && values.change > target.quantity) {
        message.warning(`库存不足，当前库存 ${target.quantity} ${target.unit || 'g'}`);
        return;
      }
      mutation.mutate({ medicineId: target.medicine_id, form: values });
    } catch {
      // 校验失败
    }
  };

  const columns: ColumnsType<Inventory> = [
    { title: '药材', dataIndex: 'medicine_name', key: 'medicine_name', width: 140 },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (c: string) => (c ? <Tag color="blue">{c}</Tag> : '-'),
    },
    {
      title: '库存量',
      key: 'quantity',
      width: 120,
      render: (_v, r) => {
        const low = r.quantity <= r.min_stock;
        return (
          <span style={{ color: low ? '#dc2626' : undefined, fontWeight: low ? 600 : 400 }}>
            {r.quantity} {r.unit}
          </span>
        );
      },
    },
    { title: '最低库存', dataIndex: 'min_stock', key: 'min_stock', width: 110 },
    {
      title: '单价',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      align: 'right',
      render: (p: number) => `¥${p.toFixed(2)}`,
    },
    {
      title: '库存价值',
      key: 'value',
      width: 120,
      align: 'right',
      render: (_v, r) => `¥${(r.quantity * r.price).toFixed(2)}`,
    },
    { title: '备注', dataIndex: 'notes', key: 'notes', ellipsis: true },
    {
      title: '操作',
      key: 'action',
      width: 220,
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
        <p className="page-subtitle">查看库存状态，进行入库 / 出库操作，低库存自动预警</p>
      </div>

      {/* 库存概览统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card size="small">
            <Statistic
              title="在库品种"
              value={stats.total}
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
          <Segmented<FilterMode>
            value={filterMode}
            onChange={(v) => setFilterMode(v)}
            options={[
              { label: '全部', value: 'all' },
              { label: `低库存${stats.lowCount > 0 ? ` (${stats.lowCount})` : ''}`, value: 'low' },
              { label: `零库存${stats.zeroCount > 0 ? ` (${stats.zeroCount})` : ''}`, value: 'zero' },
            ]}
          />
          <Input.Search
            placeholder="搜索药材名或分类"
            allowClear
            style={{ width: 260 }}
            onSearch={setKeyword}
          />
        </Space>
        <Table<Inventory>
          rowKey="id"
          loading={isLoading}
          columns={columns}
          dataSource={filteredData}
          scroll={{ x: 1100 }}
          pagination={{ pageSize: 15, showSizeChanger: true }}
          locale={{
            emptyText: `无${
              filterMode === 'low' ? '低库存' : filterMode === 'zero' ? '零库存' : ''
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
      >
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
                  {historyTarget.quantity} {historyTarget.unit}
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
