import { useMemo, useState } from 'react';
import { keepPreviousData, useQuery } from '@tanstack/react-query';
import {
  Button,
  Descriptions,
  Grid,
  Drawer,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { DeleteOutlined, EditOutlined, ExportOutlined, EyeOutlined, PlusOutlined } from '@ant-design/icons';
import {
  createMedicine,
  deleteMedicine,
  listInventory,
  listMedicines,
  updateMedicine,
} from '@/api/tauri';
import type { Medicine } from '@/types';
import EmptyState from '@/components/EmptyState';
import LoadingCard from '@/components/LoadingCard';
import QueryErrorAlert from '@/components/QueryErrorAlert';
import { useCrudMutations } from '@/hooks/useCrudMutations';
import { useCsvExport } from '@/hooks/useCsvExport';
import { aggregateInventory } from '@/utils/inventory';

const { Text } = Typography;

const { TextArea } = Input;

/** 药性下拉选项 */
const NATURE_OPTIONS = ['寒', '热', '温', '凉', '平'].map((c) => ({ label: c, value: c }));

/** 分类下拉选项（常见分类） */
const CATEGORY_OPTIONS = [
  '解表药',
  '清热药',
  '泻下药',
  '祛风湿药',
  '化湿药',
  '利水渗湿药',
  '温里药',
  '理气药',
  '消食药',
  '驱虫药',
  '止血药',
  '活血化瘀药',
  '化痰止咳平喘药',
  '安神药',
  '平肝息风药',
  '开窍药',
  '补虚药',
  '收涩药',
  '攻毒杀虫止痒药',
  '拔毒化腐生肌药',
].map((c) => ({ label: c, value: c }));

export default function MedicineList() {
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [nature, setNature] = useState<string | undefined>(undefined);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Medicine | null>(null);
  const [form] = Form.useForm<Medicine>();
  // 详情 Drawer 状态
  const [detailMedicine, setDetailMedicine] = useState<Medicine | null>(null);

  // CSV 导出：复用统一 hook
  const { exportCsv } = useCsvExport({ filenamePrefix: 'medicines_export', label: '药材记录' });

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['medicines', keyword, category, nature],
    queryFn: () => listMedicines(keyword || undefined, category, nature),
    // 药材库变更频率低，缓存 5 分钟；CRUD 后由 useCrudMutations 失效
    staleTime: 5 * 60 * 1000,
    // 搜索/筛选切换时保留上一次结果，避免表格闪烁；仅搜索列表场景使用
    placeholderData: keepPreviousData,
  });

  // 获取库存数据用于显示库存量与最低库存列
  const { data: inventoryData } = useQuery({
    queryKey: ['inventory'],
    queryFn: listInventory,
    staleTime: 60 * 1000,
  });

  // 按药材 ID 聚合库存（跨批次合并），复用统一口径工具
  const stockMap = useMemo(() => aggregateInventory(inventoryData ?? []), [inventoryData]);

  const { create: createMutation, update: updateMutation, remove: deleteMutation } =
    useCrudMutations<Medicine>({
      queryKey: ['medicines'],
      invalidateKeys: [['dashboard'], ['inventory'], ['expiring-batches']],
      createFn: createMedicine,
      updateFn: updateMedicine,
      deleteFn: deleteMedicine,
      messages: { created: '药材已添加', updated: '药材已更新', deleted: '药材已删除' },
      onClose: () => setModalOpen(false),
    });

  const categories = useMemo(() => {
    const set = new Set<string>();
    data?.forEach((m) => m.category && set.add(m.category));
    return Array.from(set);
  }, [data]);

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEdit = (record: Medicine) => {
    setEditing(record);
    form.setFieldsValue({ ...record });
    setModalOpen(true);
  };

  // 导出药材库 CSV（含完整字段，便于备份或外部维护）
  const handleExportCsv = async () => {
    const list = data ?? [];
    const rows: (string | number | null | undefined)[][] = [
      ['名称', '别名', '分类', '性', '味', '归经', '功效', '主治', '用法', '用量', '禁忌', '备注'],
    ];
    for (const m of list) {
      rows.push([
        m.name,
        m.alias ?? '',
        m.category ?? '',
        m.nature ?? '',
        m.taste ?? '',
        m.meridian ?? '',
        m.efficacy ?? '',
        m.indications ?? '',
        m.usage ?? '',
        m.dosage ?? '',
        m.contraindication ?? '',
        m.notes ?? '',
      ]);
    }
    await exportCsv(rows, list.length);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editing?.id) {
        updateMutation.mutate({ ...values, id: editing.id });
      } else {
        createMutation.mutate({ ...values, id: null });
      }
    } catch {
      // 校验失败由表单自身提示
    }
  };

  // 响应式列：按视口断点分级显示（高分屏缩放后 CSS 视口显著变窄）
  const screens = Grid.useBreakpoint();
  const showXl = !!screens.xl; // ≥1200：+ 用量/库存量
  const showXxl = !!screens.xxl; // ≥1600：+ 最低库存

  // 主表精简：低频长文本列（别名/归经/主治/禁忌/用法）下沉到行展开与详情抽屉
  const columns: ColumnsType<Medicine> = [
    {
      title: '名称 / 别名',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      fixed: 'left',
      render: (_v, r) => (
        <>
          <div style={{ fontWeight: 600 }}>{r.name}</div>
          {r.alias && (
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{r.alias}</div>
          )}
        </>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (c: string) => (c ? <Tag color="blue">{c}</Tag> : '-'),
    },
    { title: '性味', key: 'nature_taste', width: 100, render: (_v, r) => `${r.nature ?? ''} ${r.taste ?? ''}`.trim() || '-' },
    { title: '功效', dataIndex: 'efficacy', key: 'efficacy', ellipsis: { showTitle: true } },
    ...(showXl
      ? [{ title: '用量', dataIndex: 'dosage', key: 'dosage', width: 100, ellipsis: true }]
      : []),
    ...(showXl
      ? [{
          title: '库存量',
          key: 'stock_qty',
          width: 100,
          align: 'right' as const,
          sorter: (a: Medicine, b: Medicine) => {
            const sa = stockMap.get(a.id!)?.totalQty ?? 0;
            const sb = stockMap.get(b.id!)?.totalQty ?? 0;
            return sa - sb;
          },
          render: (_v: unknown, r: Medicine) => {
            const s = stockMap.get(r.id!);
            // 单位取药材首批次的实际单位（g/包/盒等），不再硬编码
            return s ? `${s.totalQty.toFixed(1)} ${s.unit}` : '-';
          },
        }]
      : []),
    ...(showXxl
      ? [{
          title: '最低库存',
          key: 'min_stock',
          width: 90,
          align: 'right' as const,
          render: (_v: unknown, r: Medicine) => {
            const s = stockMap.get(r.id!);
            return s ? `${s.minStock.toFixed(1)}` : '-';
          },
        }]
      : []),
    {
      title: '操作',
      key: 'action',
      width: 130,
      fixed: 'right',
      render: (_v, record) => (
        <Space size={2}>
          <Tooltip title="详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => setDetailMedicine(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => openEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确认删除该药材？"
            description="删除后将级联清除其库存记录"
            onConfirm={() => deleteMutation.mutate(record.id!)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="删除">
              <Button type="text" size="small" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">药材管理</h1>
        <p className="page-subtitle">维护药材基础信息：性味、归经、功效、用法用量、禁忌等</p>
      </div>

      <div className="table-card">
        {isError && (
          <QueryErrorAlert
            error={error}
            onRetry={() => refetch()}
            retrying={isFetching}
            message="加载药材列表失败"
          />
        )}
        <Space style={{ marginBottom: 16 }} wrap>
          <Input.Search
            placeholder="搜索药材名 / 别名 / 功效"
            allowClear
            style={{ width: 260 }}
            onSearch={setKeyword}
          />
          <Select
            placeholder="选择分类"
            allowClear
            style={{ width: 140 }}
            options={[...categories, ...CATEGORY_OPTIONS.map((o) => o.value)]
              .filter((v, i, arr) => arr.indexOf(v) === i)
              .map((c) => ({ label: c, value: c }))}
            onChange={(v) => setCategory(v)}
          />
          <Select
            placeholder="药性"
            allowClear
            style={{ width: 100 }}
            options={NATURE_OPTIONS}
            onChange={(v) => setNature(v)}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            新增药材
          </Button>
          <Button
            icon={<ExportOutlined />}
            onClick={handleExportCsv}
            disabled={!data || data.length === 0}
          >
            导出 CSV
          </Button>
        </Space>

        {isLoading && !data ? (
          <LoadingCard title="药材列表" height={400} />
        ) : (
          <Table<Medicine>
            rowKey="id"
            columns={columns}
            dataSource={data}
            scroll={{ x: showXxl ? 860 : showXl ? 780 : 560 }}
            pagination={{ pageSize: 15, showSizeChanger: true }}
            onRow={(record) => ({
              onDoubleClick: () => setDetailMedicine(record),
            })}
            expandable={{
              // 下沉到展开行的长文本：归经 / 主治 / 用法 / 禁忌（别名已并入名称列）
              rowExpandable: (r) =>
                Boolean(r.meridian || r.indications || r.contraindication || r.usage),
              expandedRowRender: (r) => (
                <Descriptions size="small" column={2} style={{ margin: 0 }}>
                  <Descriptions.Item label="归经">{r.meridian || '-'}</Descriptions.Item>
                  <Descriptions.Item label="用法">{r.usage || '-'}</Descriptions.Item>
                  <Descriptions.Item label="主治" span={r.indications ? 2 : 1}>
                    {r.indications ? (
                      <span style={{ whiteSpace: 'pre-wrap' }}>{r.indications}</span>
                    ) : (
                      '-'
                    )}
                  </Descriptions.Item>
                  <Descriptions.Item label="禁忌" span={r.contraindication ? 2 : 1}>
                    {r.contraindication ? (
                      <span style={{ whiteSpace: 'pre-wrap', color: 'var(--danger-color)' }}>
                        {r.contraindication}
                      </span>
                    ) : (
                      '-'
                    )}
                  </Descriptions.Item>
                </Descriptions>
              ),
            }}
            locale={{
              emptyText: (
                <EmptyState
                  title={keyword || category ? '未找到匹配药材' : '暂无药材'}
                  description={
                    keyword || category
                      ? '尝试更换关键字或清除筛选条件'
                      : '点击「新增药材」开始录入药材基础信息'
                  }
                  action={
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={openCreate}
                    >
                      新增药材
                    </Button>
                  }
                />
              ),
            }}
          />
        )}
      </div>

      <Modal
        title={editing ? '编辑药材' : '新增药材'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        okText="保存"
        cancelText="取消"
        width={680}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入药材名称' }]}
          >
            <Input placeholder="如：人参" />
          </Form.Item>
          <Form.Item name="alias" label="别名">
            <Input placeholder="多个别名用逗号分隔" />
          </Form.Item>
          <Form.Item name="category" label="分类">
            <Select
              placeholder="选择分类"
              allowClear
              showSearch
              options={CATEGORY_OPTIONS}
            />
          </Form.Item>
          <Space style={{ display: 'flex' }} size="middle">
            <Form.Item name="nature" label="性" style={{ flex: 1 }}>
              <Input placeholder="如：温" />
            </Form.Item>
            <Form.Item name="taste" label="味" style={{ flex: 1 }}>
              <Input placeholder="如：甘、苦" />
            </Form.Item>
            <Form.Item name="meridian" label="归经" style={{ flex: 1 }}>
              <Input placeholder="如：脾、肺经" />
            </Form.Item>
          </Space>
          <Form.Item name="efficacy" label="功效">
            <TextArea autoSize={{ minRows: 2 }} />
          </Form.Item>
          <Form.Item name="indications" label="主治">
            <TextArea autoSize={{ minRows: 2 }} />
          </Form.Item>
          <Space style={{ display: 'flex' }} size="middle">
            <Form.Item name="usage" label="用法" style={{ flex: 1 }}>
              <Input />
            </Form.Item>
            <Form.Item name="dosage" label="用量" style={{ flex: 1 }}>
              <Input placeholder="如：3-9g" />
            </Form.Item>
          </Space>
          <Form.Item name="contraindication" label="禁忌">
            <TextArea autoSize={{ minRows: 1 }} />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <TextArea autoSize={{ minRows: 1 }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 药材详情 Drawer（只读） */}
      <Drawer
        title={detailMedicine ? `药材详情：${detailMedicine.name}` : '药材详情'}
        open={!!detailMedicine}
        onClose={() => setDetailMedicine(null)}
        width={560}
      >
        {detailMedicine && (
          <Descriptions column={2} size="small" bordered>
            <Descriptions.Item label="名称">
              <Text strong>{detailMedicine.name}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="别名">
              {detailMedicine.alias || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="分类">
              {detailMedicine.category ? (
                <Tag color="blue">{detailMedicine.category}</Tag>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="性味">
              {[detailMedicine.nature, detailMedicine.taste]
                .filter(Boolean)
                .join(' ') || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="归经" span={2}>
              {detailMedicine.meridian || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="功效" span={2}>
              {detailMedicine.efficacy ? (
                <Text style={{ whiteSpace: 'pre-wrap' }}>
                  {detailMedicine.efficacy}
                </Text>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="主治" span={2}>
              {detailMedicine.indications ? (
                <Text style={{ whiteSpace: 'pre-wrap' }}>
                  {detailMedicine.indications}
                </Text>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="用法">
              {detailMedicine.usage || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="用量">
              {detailMedicine.dosage || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="禁忌" span={2}>
              {detailMedicine.contraindication ? (
                <Text type="danger" style={{ whiteSpace: 'pre-wrap' }}>
                  {detailMedicine.contraindication}
                </Text>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="备注" span={2}>
              {detailMedicine.notes ? (
                <Text style={{ whiteSpace: 'pre-wrap' }}>
                  {detailMedicine.notes}
                </Text>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {detailMedicine.created_at || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="更新时间">
              {detailMedicine.updated_at || '-'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </div>
  );
}
