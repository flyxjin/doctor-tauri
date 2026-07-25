import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  App,
  Button,
  Descriptions,
  Drawer,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { DeleteOutlined, EditOutlined, ExportOutlined, EyeOutlined, PlusOutlined } from '@ant-design/icons';
import {
  createMedicine,
  deleteMedicine,
  listMedicines,
  saveTextToDownloads,
  updateMedicine,
} from '@/api/tauri';
import type { Medicine } from '@/types';
import EmptyState from '@/components/EmptyState';
import LoadingCard from '@/components/LoadingCard';
import { useCrudMutations } from '@/hooks/useCrudMutations';
import { rowsToCsv } from '@/utils/csv';
import { formatError } from '@/utils/formatError';

const { Text } = Typography;

const { TextArea } = Input;

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
  const { message } = App.useApp();
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Medicine | null>(null);
  const [form] = Form.useForm<Medicine>();
  // 详情 Drawer 状态
  const [detailMedicine, setDetailMedicine] = useState<Medicine | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['medicines', keyword, category],
    queryFn: () => listMedicines(keyword || undefined, category),
    // 药材库变更频率低，缓存 5 分钟；CRUD 后由 useCrudMutations 失效
    staleTime: 5 * 60 * 1000,
  });

  const { create: createMutation, update: updateMutation, remove: deleteMutation } =
    useCrudMutations<Medicine>({
      queryKey: ['medicines'],
      invalidateKeys: [['dashboard'], ['inventory']],
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
    if (list.length === 0) {
      message.warning('没有可导出的数据');
      return;
    }
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
    const csv = rowsToCsv(rows);
    try {
      const ts = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      const path = await saveTextToDownloads(`medicines_export_${ts}.csv`, csv);
      message.success(`已导出 ${list.length} 条药材记录到：${path}`);
    } catch (e) {
      message.error(formatError(e));
    }
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

  const columns: ColumnsType<Medicine> = [
    { title: '名称', dataIndex: 'name', key: 'name', width: 100, fixed: 'left' },
    { title: '别名', dataIndex: 'alias', key: 'alias', width: 120, ellipsis: true },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (c: string) => (c ? <Tag color="blue">{c}</Tag> : '-'),
    },
    { title: '性味', key: 'nature_taste', width: 120, render: (_v, r) => `${r.nature ?? ''} ${r.taste ?? ''}`.trim() || '-' },
    { title: '归经', dataIndex: 'meridian', key: 'meridian', width: 140, ellipsis: true },
    { title: '功效', dataIndex: 'efficacy', key: 'efficacy', ellipsis: true },
    { title: '用量', dataIndex: 'dosage', key: 'dosage', width: 120, ellipsis: true },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_v, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => setDetailMedicine(record)}
          >
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => openEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除该药材？"
            description="删除后将级联清除其库存记录"
            onConfirm={() => deleteMutation.mutate(record.id!)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
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
            style={{ width: 160 }}
            options={[...categories, ...CATEGORY_OPTIONS.map((o) => o.value)]
              .filter((v, i, arr) => arr.indexOf(v) === i)
              .map((c) => ({ label: c, value: c }))}
            onChange={(v) => setCategory(v)}
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
            scroll={{ x: 1200 }}
            pagination={{ pageSize: 15, showSizeChanger: true }}
            onRow={(record) => ({
              onDoubleClick: () => setDetailMedicine(record),
            })}
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
          <Descriptions column={1} size="small" bordered>
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
            <Descriptions.Item label="归经">
              {detailMedicine.meridian || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="功效">
              {detailMedicine.efficacy ? (
                <Text style={{ whiteSpace: 'pre-wrap' }}>
                  {detailMedicine.efficacy}
                </Text>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="主治">
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
            <Descriptions.Item label="禁忌">
              {detailMedicine.contraindication ? (
                <Text type="danger" style={{ whiteSpace: 'pre-wrap' }}>
                  {detailMedicine.contraindication}
                </Text>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="备注">
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
