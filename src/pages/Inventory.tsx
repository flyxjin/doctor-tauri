import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Alert,
  App,
  Button,
  Col,
  Descriptions,
  Grid,
  DatePicker,
  Drawer,
  Form,
  Input,
  InputNumber,
  Modal,
  Radio,
  Row,
  Segmented,
  Select,
  Space,
  Table,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import {
  ClockCircleOutlined,
  DollarOutlined,
  ExclamationCircleOutlined,
  ExportOutlined,
  HistoryOutlined,
  ImportOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Dayjs } from 'dayjs';
import {
  listExpiringBatches,
  listInventory,
  listInventoryHistory,
  updateStock,
  adjustStock,
  updateInventoryPrice,
  batchUpdatePrice,
} from '@/api/tauri';
import { formatError } from '@/utils/formatError';
import {
  EXPIRY_WARN_DAYS,
  aggregateInventory,
  expiryStatus,
} from '@/utils/inventory';
import { useCsvExport } from '@/hooks/useCsvExport';
import QueryErrorAlert from '@/components/QueryErrorAlert';
import StatCard from '@/components/StatCard';
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

interface AdjustForm {
  target_quantity: number;
  operator?: string;
  notes?: string;
}

type FilterMode = 'all' | 'low' | 'zero' | 'expiring';

export default function InventoryPage() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [form] = Form.useForm<StockForm>();
  const [modalOpen, setModalOpen] = useState(false);
  const [target, setTarget] = useState<Inventory | null>(null);
  const [filterMode, setFilterMode] = useState<FilterMode>('all');
  const [keyword, setKeyword] = useState('');
  const [historyTarget, setHistoryTarget] = useState<Inventory | null>(null);
  const [adjustTarget, setAdjustTarget] = useState<Inventory | null>(null);
  const [adjustForm] = Form.useForm<AdjustForm>();

  // CSV 导出：复用统一 hook（统一用 \r\n 行分隔符，避免 Excel 兼容性问题）
  const { exportCsv } = useCsvExport({ filenamePrefix: 'inventory_export', label: '库存记录' });

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['inventory'],
    queryFn: listInventory,
    // 库存变更频率中等，缓存 1 分钟；出入库后由 mutation 失效
    staleTime: 60 * 1000,
  });

  // 效期预警批次（30 天内到期或已过期）
  const { data: expiringData } = useQuery({
    queryKey: ['expiring-batches', EXPIRY_WARN_DAYS],
    queryFn: () => listExpiringBatches(EXPIRY_WARN_DAYS),
    staleTime: 60 * 1000,
  });

  // 库存变更历史（仅当选择某药材时查询）
  const {
    data: historyData,
    isLoading: historyLoading,
    isError: historyIsError,
    error: historyError,
    refetch: historyRefetch,
    isFetching: historyFetching,
  } = useQuery({
    queryKey: ['inventory-history', historyTarget?.medicine_id],
    queryFn: () => listInventoryHistory(historyTarget!.medicine_id, undefined, undefined, undefined, 100),
    enabled: !!historyTarget,
  });

  // 按药材聚合的汇总（一药多批后统计口径需跨批次合并）
  const medicineSummary = useMemo(() => aggregateInventory(data ?? []), [data]);

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
      queryClient.invalidateQueries({ queryKey: ['expiring-batches'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      // 历史抽屉的 30 秒 staleTime 内可能看不到刚写入的变更，主动失效
      queryClient.invalidateQueries({ queryKey: ['inventory-history'] });
      setModalOpen(false);
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  // 库存调整 mutation
  const adjustMutation = useMutation({
    mutationFn: (vars: { inventoryId: number; form: AdjustForm }) =>
      adjustStock(
        vars.inventoryId,
        vars.form.target_quantity,
        vars.form.operator,
        vars.form.notes,
      ),
    onSuccess: () => {
      message.success('库存调整成功');
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['expiring-batches'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-history'] });
      setAdjustTarget(null);
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  // 行内改价：单价列直接编辑，立即生效并记操作日志
  const priceMutation = useMutation({
    mutationFn: (vars: { inventoryId: number; price: number }) =>
      updateInventoryPrice(vars.inventoryId, vars.price),
    onSuccess: () => {
      message.success('单价已更新');
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  // 批量调价弹窗状态
  const [priceModalOpen, setPriceModalOpen] = useState(false);
  const [priceCategory, setPriceCategory] = useState('');
  const [priceMode, setPriceMode] = useState<'set' | 'percent'>('set');
  const [priceValue, setPriceValue] = useState<number | null>(null);

  const batchPriceMutation = useMutation({
    mutationFn: (vars: { category: string; mode: 'set' | 'percent'; value: number }) =>
      batchUpdatePrice(vars.category, vars.mode, vars.value),
    onSuccess: (affected, vars) => {
      message.success(
        vars.mode === 'set'
          ? `已将「${vars.category}」${affected} 个批次单价设为 ¥${vars.value.toFixed(2)}/g`
          : `已将「${vars.category}」${affected} 个批次单价调整 ${vars.value > 0 ? '+' : ''}${vars.value}%`,
      );
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setPriceModalOpen(false);
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  const handleBatchPriceSubmit = () => {
    if (!priceCategory) {
      message.warning('请选择药材分类');
      return;
    }
    if (priceValue === null) {
      message.warning(priceMode === 'set' ? '请输入目标单价' : '请输入调整幅度');
      return;
    }
    batchPriceMutation.mutate({ category: priceCategory, mode: priceMode, value: priceValue });
  };

  // 分类下拉选项（来自当前库存数据，去重排序）
  const categoryOptions = useMemo(
    () =>
      [...new Set((data ?? []).map((r) => r.category).filter(Boolean))].sort().map((c) => ({
        label: c,
        value: c,
      })),
    [data],
  );

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

  // 导出当前筛选后的库存为 CSV（行分隔符由 hook 统一为 \r\n，Excel 友好）
  const handleExportCsv = async () => {
    const list = filteredData;
    const rows: (string | number | null | undefined)[][] = [
      ['药材', '分类', '批次号', '生产日期', '效期', '库存量', '单位', '最低库存', '单价', '批次价值', '备注'],
    ];
    for (const i of list) {
      rows.push([
        i.medicine_name,
        i.category,
        i.batch_no,
        i.production_date,
        i.expiry_date,
        i.quantity,
        i.unit,
        i.min_stock,
        i.price.toFixed(2),
        (i.quantity * i.price).toFixed(2),
        i.notes,
      ]);
    }
    await exportCsv(rows, list.length);
  };

  // 订阅 is_in 字段变化，使 Modal 标题与批次输入区随操作类型切换
  const isInWatch = Form.useWatch('is_in', form);

  const handleAdjustSubmit = async () => {
    if (!adjustTarget) return;
    try {
      const values = await adjustForm.validateFields();
      if (values.target_quantity < 0) {
        message.warning('目标库存不能为负数');
        return;
      }
      adjustMutation.mutate({ inventoryId: adjustTarget.id!, form: values });
    } catch {
      // 校验失败
    }
  };

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

  // 响应式列：按视口断点分级显示（高分屏缩放后 CSS 视口会显著变窄）
  // 各档合计（含行展开图标列 48px）均小于对应断点的可用宽度，杜绝横向滚动
  const screens = Grid.useBreakpoint();
  const showLg = !!screens.lg; // ≥992：+ 分类
  const showXl = !!screens.xl; // ≥1200：+ 批次号/最低库存/单价
  const showXxl = !!screens.xxl; // ≥1600：+ 批次价值

  // 主表精简：备注下沉到行展开，操作列图标化
  const columns: ColumnsType<Inventory> = [
    { title: '药材', dataIndex: 'medicine_name', key: 'medicine_name', width: 110, fixed: 'left', ellipsis: true },
    ...(showLg
      ? [{
          title: '分类',
          dataIndex: 'category',
          key: 'category',
          width: 90,
          render: (c: string) => (c ? <Tag color="blue">{c}</Tag> : '-'),
        }]
      : []),
    ...(showXl
      ? [{
          title: '批次号',
          dataIndex: 'batch_no',
          key: 'batch_no',
          width: 104,
          ellipsis: true,
          render: (b: string) => b || <Text type="secondary">—</Text>,
        }]
      : []),
    {
      title: '效期',
      dataIndex: 'expiry_date',
      key: 'expiry_date',
      width: 110,
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
      width: 105,
      render: (_v, r) => {
        const low = r.quantity <= r.min_stock;
        return (
          // 使用 CSS 变量，深色主题下保持可读对比度
          <span style={{ color: low ? 'var(--danger-color)' : undefined, fontWeight: low ? 600 : 400 }}>
            {r.quantity} {r.unit}
          </span>
        );
      },
    },
    ...(showXl
      ? [{ title: '最低库存', dataIndex: 'min_stock', key: 'min_stock', width: 90 }]
      : []),
    ...(showXl
      ? [{
          title: '单价',
          dataIndex: 'price',
          key: 'price',
          width: 110,
          align: 'right' as const,
          render: (p: number, record: Inventory) => (
            <InputNumber
              key={`${record.id}:${record.price}`}
              size="small"
              min={0}
              step={0.1}
              defaultValue={Number(p.toFixed(2))}
              style={{ width: 96 }}
              onBlur={(e) => {
                const raw = (e.target as HTMLInputElement).value.trim();
                if (!raw) return;
                const v = Number(raw);
                if (!Number.isFinite(v) || Math.abs(v - p) < 0.005) return;
                priceMutation.mutate({ inventoryId: record.id!, price: v });
              }}
            />
          ),
        }]
      : []),
    ...(showXxl
      ? [{
          title: '批次价值',
          key: 'value',
          width: 100,
          align: 'right' as const,
          render: (_v: unknown, r: Inventory) => `¥${(r.quantity * r.price).toFixed(2)}`,
        }]
      : []),
    {
      title: '操作',
      key: 'action',
      width: 158,
      fixed: 'right',
      render: (_v, record) => (
        <Space size={2}>
          <Tooltip title="入库">
            <Button
              type="text"
              size="small"
              icon={<ImportOutlined />}
              onClick={() => openModal(record, true)}
            />
          </Tooltip>
          <Tooltip title="出库">
            <Button
              type="text"
              size="small"
              danger
              icon={<ExportOutlined />}
              onClick={() => openModal(record, false)}
            />
          </Tooltip>
          <Tooltip title="变更历史">
            <Button
              type="text"
              size="small"
              icon={<HistoryOutlined />}
              onClick={() => setHistoryTarget(record)}
            />
          </Tooltip>
          <Tooltip title="库存调整（盘点）">
            <Button
              type="text"
              size="small"
              icon={<ToolOutlined />}
              onClick={() => {
                setAdjustTarget(record);
                adjustForm.resetFields();
                adjustForm.setFieldsValue({ target_quantity: record.quantity });
              }}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 行展开：备注 + 被响应式隐藏的低优先字段（窄视口下主表不显示但信息不丢）
  const expandedRowRenderInv = (r: Inventory) => (
    <Descriptions size="small" column={2} style={{ margin: 0 }}>
      {!showXl && <Descriptions.Item label="批次号">{r.batch_no || '—'}</Descriptions.Item>}
      {!showXl && (
        <Descriptions.Item label="最低库存">{r.min_stock}</Descriptions.Item>
      )}
      {!showXl && (
        <Descriptions.Item label="单价">
          {`¥${r.price.toFixed(2)}`}
        </Descriptions.Item>
      )}
      {!showXxl && (
        <Descriptions.Item label="批次价值">
          {`¥${(r.quantity * r.price).toFixed(2)}`}
        </Descriptions.Item>
      )}
      <Descriptions.Item label="备注" span={2}>
        {r.notes || '—'}
      </Descriptions.Item>
    </Descriptions>
  );

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
      width: 86,
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

      {/* 库存概览统计卡（统一 StatCard，深浅主题自动适配） */}
      <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 16 }}>
        <StatCard
          title="在库品种"
          value={stats.totalKinds}
          suffix="种"
          loading={isLoading}
          variant="success"
        />
        <StatCard
          title="低库存预警"
          value={stats.lowCount}
          suffix="种"
          loading={isLoading}
          variant={stats.lowCount > 0 ? 'warning' : 'default'}
        />
        <StatCard
          title="零库存"
          value={stats.zeroCount}
          suffix="种"
          loading={isLoading}
          variant={stats.zeroCount > 0 ? 'warning' : 'default'}
        />
        <StatCard
          title="库存总价值"
          value={stats.totalValue}
          precision={2}
          prefix="¥"
          loading={isLoading}
          variant="accent"
        />
      </div>

      <div className="table-card">
        {isError && (
          <QueryErrorAlert
            error={error}
            onRetry={() => refetch()}
            retrying={isFetching}
            message="加载库存数据失败"
          />
        )}
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
          <Space>
            <Button icon={<DollarOutlined />} onClick={() => setPriceModalOpen(true)}>
              批量调价
            </Button>
            <Button
              icon={<ExportOutlined />}
              onClick={handleExportCsv}
              disabled={filteredData.length === 0}
            >
              导出 CSV
            </Button>
          </Space>
        </Space>
        <Table<Inventory>
          rowKey="id"
          loading={isLoading}
          columns={columns}
          dataSource={filteredData}
          scroll={{ x: showXxl ? 916 : showXl ? 730 : showLg ? 621 : 531 }}
          expandable={{
            // 备注与被响应式隐藏的字段下沉到行展开
            rowExpandable: () => true,
            expandedRowRender: expandedRowRenderInv,
          }}
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
            <InputNumber min={0.01} step={1} style={{ width: '100%' }} />
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

      {/* 库存调整 Modal */}
      <Modal
        title={`${adjustTarget?.medicine_name ?? ''} - 库存调整`}
        open={!!adjustTarget}
        onOk={handleAdjustSubmit}
        onCancel={() => setAdjustTarget(null)}
        confirmLoading={adjustMutation.isPending}
        okText="确认调整"
        cancelText="取消"
        width={480}
      >
        {adjustTarget && (
          <Alert
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
            message={
              <span>
                当前库存：
                <Text strong style={{ fontSize: 16 }}>
                  {adjustTarget.quantity} {adjustTarget.unit}
                </Text>
                <Text type="secondary" style={{ marginLeft: 12 }}>
                  批次余量：{adjustTarget.quantity} {adjustTarget.unit}
                </Text>
              </span>
            }
            description="将库存调整为目标数量，差值自动记入变更历史（盘盈记为入库，盘亏记为出库）"
          />
        )}
        <Form form={adjustForm} layout="vertical" preserve={false}>
          <Form.Item
            name="target_quantity"
            label="目标库存量"
            rules={[{ required: true, message: '请输入目标库存量' }]}
          >
            <InputNumber min={0} step={1} style={{ width: '100%' }} addonAfter={adjustTarget?.unit ?? 'g'} />
          </Form.Item>
          <Form.Item name="operator" label="操作人">
            <Input placeholder="操作人姓名" />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <Input.TextArea autoSize={{ minRows: 2 }} placeholder="调整原因，如：盘点核实" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 批量调价弹窗 */}
      <Modal
        title="按分类批量调价"
        open={priceModalOpen}
        onOk={handleBatchPriceSubmit}
        onCancel={() => setPriceModalOpen(false)}
        confirmLoading={batchPriceMutation.isPending}
        okText="确认调价"
        cancelText="取消"
        width={460}
      >
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          message="批量调价立即生效并记入操作日志"
          description="影响所选分类下的全部库存批次；百分比浮动仅对现价大于 0 的批次生效。"
        />
        <Form layout="vertical">
          <Form.Item label="药材分类" required>
            <Select
              placeholder="选择分类"
              style={{ width: '100%' }}
              showSearch
              value={priceCategory || undefined}
              options={categoryOptions}
              onChange={(v) => setPriceCategory(v ?? '')}
            />
          </Form.Item>
          <Form.Item label="调价方式" required>
            <Radio.Group value={priceMode} onChange={(e) => setPriceMode(e.target.value)}>
              <Radio.Button value="set">设为固定价</Radio.Button>
              <Radio.Button value="percent">按百分比浮动</Radio.Button>
            </Radio.Group>
          </Form.Item>
          <Form.Item label={priceMode === 'set' ? '目标单价（元/g）' : '调整幅度（%）'} required>
            <InputNumber
              min={priceMode === 'set' ? 0 : -95}
              max={priceMode === 'set' ? 1_000_000 : 500}
              step={priceMode === 'set' ? 0.1 : 1}
              value={priceValue}
              onChange={(v) => setPriceValue(v)}
              style={{ width: '100%' }}
              addonAfter={priceMode === 'set' ? '元/g' : '%'}
            />
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
            {historyIsError && (
              <QueryErrorAlert
                error={historyError}
                onRetry={() => historyRefetch()}
                retrying={historyFetching}
                message="加载库存变更历史失败"
              />
            )}
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
