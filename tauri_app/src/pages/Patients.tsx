import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  App,
  Button,
  Card,
  Col,
  Descriptions,
  Drawer,
  Empty,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Select,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  CopyOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  PlusOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import {
  createPatient,
  deletePatient,
  getPatientStatistics,
  listPatients,
  listPrescriptions,
  updatePatient,
} from '@/api/tauri';
import type { Patient, PrescriptionWithItems } from '@/types';
import { PRESCRIPTION_COPY_KEY } from '@/pages/History';
import EmptyState from '@/components/EmptyState';
import LoadingCard from '@/components/LoadingCard';
import { useCrudMutations } from '@/hooks/useCrudMutations';

const { TextArea } = Input;
const { Title, Text } = Typography;

/** 性别下拉选项 */
const GENDER_OPTIONS = [
  { label: '男', value: '男' },
  { label: '女', value: '女' },
  { label: '其他', value: '其他' },
];

export default function Patients() {
  const [keyword, setKeyword] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Patient | null>(null);
  const [form] = Form.useForm<Patient>();

  // 详情 Drawer 状态
  const [detailPatient, setDetailPatient] = useState<Patient | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['patients', keyword],
    queryFn: () => listPatients(keyword || undefined),
  });

  const { create: createMutation, update: updateMutation, remove: deleteMutation } =
    useCrudMutations<Patient>({
      queryKey: ['patients'],
      invalidateKeys: [['dashboard']],
      createFn: createPatient,
      updateFn: updatePatient,
      deleteFn: deletePatient,
      messages: {
        created: '患者已添加',
        updated: '患者信息已更新',
        deleted: '患者已删除',
      },
      onClose: () => setModalOpen(false),
    });

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEdit = (record: Patient) => {
    setEditing(record);
    form.setFieldsValue({ ...record });
    setModalOpen(true);
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

  const columns: ColumnsType<Patient> = [
    { title: '姓名', dataIndex: 'name', key: 'name', width: 100, fixed: 'left' },
    {
      title: '性别',
      dataIndex: 'gender',
      key: 'gender',
      width: 80,
      render: (g: string) => (g ? <Tag color={g === '男' ? 'blue' : 'pink'}>{g}</Tag> : '-'),
    },
    { title: '年龄', dataIndex: 'age', key: 'age', width: 80, render: (a: number | null) => a ?? '-' },
    { title: '电话', dataIndex: 'phone', key: 'phone', width: 140 },
    {
      title: '过敏史',
      dataIndex: 'allergy',
      key: 'allergy',
      width: 160,
      ellipsis: true,
      render: (a: string) =>
        a ? <Text type="danger">{a}</Text> : '-',
    },
    { title: '地址', dataIndex: 'address', key: 'address', ellipsis: true },
    { title: '建档日期', dataIndex: 'created_at', key: 'created_at', width: 180 },
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
            onClick={() => setDetailPatient(record)}
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
            title="确认删除该患者档案？"
            description="删除后无法恢复，处方历史记录将保留"
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
        <h1 className="page-title">客户管理</h1>
        <p className="page-subtitle">维护患者档案：基本信息、过敏史、既往病史，关联查看处方历史与消费统计</p>
      </div>

      {/* 统计卡片：患者总数 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={8} md={6}>
          <Card bordered={false} style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
            <Statistic
              title="患者总数"
              value={data?.length ?? 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#2D5F3F' }}
            />
          </Card>
        </Col>
      </Row>

      <div className="table-card">
        <Space style={{ marginBottom: 16 }} wrap>
          <Input.Search
            placeholder="按姓名 / 电话搜索"
            allowClear
            style={{ width: 260 }}
            onSearch={setKeyword}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            新增患者
          </Button>
        </Space>

        {isLoading && !data ? (
          <LoadingCard title="患者列表" height={400} />
        ) : (
          <Table<Patient>
            rowKey="id"
            columns={columns}
            dataSource={data}
            scroll={{ x: 1100 }}
            pagination={{ pageSize: 15, showSizeChanger: true }}
            onRow={(record) => ({
              onDoubleClick: () => setDetailPatient(record),
            })}
            locale={{
              emptyText: (
                <EmptyState
                  title={keyword ? '未找到匹配患者' : '暂无患者档案'}
                  description={
                    keyword
                      ? '尝试更换姓名或电话关键字'
                      : '点击「新增患者」开始建立患者档案'
                  }
                  action={
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={openCreate}
                    >
                      新增患者
                    </Button>
                  }
                />
              ),
            }}
          />
        )}
      </div>

      {/* 新增 / 编辑 Modal */}
      <Modal
        title={editing ? '编辑患者' : '新增患者'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        okText="保存"
        cancelText="取消"
        width={640}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" preserve={false}>
          <Space style={{ display: 'flex' }} size="middle">
            <Form.Item
              name="name"
              label="姓名"
              style={{ flex: 1 }}
              rules={[{ required: true, message: '请输入患者姓名' }]}
            >
              <Input placeholder="如：张三" />
            </Form.Item>
            <Form.Item name="gender" label="性别" style={{ width: 120 }}>
              <Select placeholder="选择性别" allowClear options={GENDER_OPTIONS} />
            </Form.Item>
            <Form.Item name="age" label="年龄" style={{ width: 120 }}>
              <InputNumber min={0} max={150} style={{ width: '100%' }} placeholder="岁" />
            </Form.Item>
          </Space>
          <Form.Item name="phone" label="联系电话">
            <Input placeholder="如：13800138000" />
          </Form.Item>
          <Form.Item name="address" label="地址">
            <Input placeholder="居住地址" />
          </Form.Item>
          <Form.Item name="allergy" label="过敏史">
            <TextArea autoSize={{ minRows: 1 }} placeholder="如：青霉素、海鲜" />
          </Form.Item>
          <Form.Item name="medical_history" label="既往病史">
            <TextArea autoSize={{ minRows: 2 }} placeholder="如：高血压、糖尿病" />
          </Form.Item>
          <Form.Item name="notes" label="备注">
            <TextArea autoSize={{ minRows: 1 }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情 Drawer */}
      <PatientDetailDrawer
        patient={detailPatient}
        onClose={() => setDetailPatient(null)}
      />
    </div>
  );
}

// ==================== 患者详情 Drawer ====================

interface PatientDetailDrawerProps {
  patient: Patient | null;
  onClose: () => void;
}

/** 患者详情 Drawer：展示基本信息、处方历史、统计数据 */
function PatientDetailDrawer({ patient, onClose }: PatientDetailDrawerProps) {
  const navigate = useNavigate();
  const { message } = App.useApp();

  // 改用 listPrescriptions 获取带 items 的处方，以支持「复制到处方」
  const { data: prescriptions, isLoading: loadingPrescriptions } = useQuery({
    queryKey: ['patient-prescriptions', patient?.name],
    queryFn: () => listPrescriptions(patient!.name, undefined, undefined, 100),
    enabled: !!patient,
  });

  const { data: statistics, isLoading: loadingStats } = useQuery({
    queryKey: ['patient-statistics', patient?.name],
    queryFn: () => getPatientStatistics(patient!.name),
    enabled: !!patient,
  });

  // 复制处方到处方页（与 History 页逻辑一致）
  const handleCopyToPrescription = (record: PrescriptionWithItems) => {
    const payload = {
      patient_name: record.patient_name,
      patient_age: record.patient_age ?? null,
      patient_gender: record.patient_gender,
      diagnosis: record.diagnosis,
      created_by: record.created_by,
      items: record.items.map((i) => ({
        medicine_id: i.medicine_id,
        medicine_name: i.medicine_name,
        quantity: i.quantity,
        unit: i.unit,
        price: i.price,
        amount: Number((i.quantity * i.price).toFixed(2)),
      })),
    };
    sessionStorage.setItem(PRESCRIPTION_COPY_KEY, JSON.stringify(payload));
    onClose();
    navigate('/prescription');
    message.success(`已加载处方 #${record.id} 的 ${record.items.length} 味药材，请核对后保存`);
  };

  const prescriptionColumns: ColumnsType<PrescriptionWithItems> = [
    { title: '处方号', dataIndex: 'id', key: 'id', width: 80 },
    { title: '诊断', dataIndex: 'diagnosis', key: 'diagnosis', ellipsis: true },
    {
      title: '金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 110,
      align: 'right',
      render: (v: number) => (
        <Tag color="blue" style={{ borderRadius: 4 }}>
          ¥{v.toFixed(2)}
        </Tag>
      ),
    },
    { title: '开方人', dataIndex: 'created_by', key: 'created_by', width: 100 },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 160 },
    {
      title: '操作',
      key: 'action',
      width: 90,
      render: (_v, record) => (
        <Button
          type="link"
          size="small"
          icon={<CopyOutlined />}
          onClick={() => handleCopyToPrescription(record)}
        >
          复制
        </Button>
      ),
    },
  ];

  return (
    <Drawer
      title={patient ? `患者详情：${patient.name}` : '患者详情'}
      open={!!patient}
      onClose={onClose}
      width={720}
    >
      {patient && (
        <>
          <Descriptions column={2} size="small" bordered>
            <Descriptions.Item label="姓名" span={1}>
              {patient.name}
            </Descriptions.Item>
            <Descriptions.Item label="性别" span={1}>
              {patient.gender || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="年龄" span={1}>
              {patient.age ?? '-'}
            </Descriptions.Item>
            <Descriptions.Item label="电话" span={1}>
              {patient.phone || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="地址" span={2}>
              {patient.address || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="过敏史" span={2}>
              {patient.allergy ? (
                <Text type="danger">{patient.allergy}</Text>
              ) : (
                '-'
              )}
            </Descriptions.Item>
            <Descriptions.Item label="既往病史" span={2}>
              {patient.medical_history || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="备注" span={2}>
              {patient.notes || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="建档日期" span={1}>
              {patient.created_at || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="更新日期" span={1}>
              {patient.updated_at || '-'}
            </Descriptions.Item>
          </Descriptions>

          {/* 统计数据 */}
          <Title level={5} style={{ marginTop: 16 }}>
            消费统计
          </Title>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="处方数"
                value={statistics?.prescription_count ?? 0}
                loading={loadingStats}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="累计金额"
                value={statistics?.total_amount ?? 0}
                precision={2}
                prefix="¥"
                loading={loadingStats}
                valueStyle={{ color: '#B83A2E' }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="首诊日期"
                value={statistics?.first_visit ?? '—'}
                loading={loadingStats}
                valueStyle={{ fontSize: 16 }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="末诊日期"
                value={statistics?.last_visit ?? '—'}
                loading={loadingStats}
                valueStyle={{ fontSize: 16 }}
              />
            </Col>
          </Row>

          {/* 处方历史 */}
          <Title level={5} style={{ marginTop: 16 }}>
            处方历史
          </Title>
          <Table<PrescriptionWithItems>
            rowKey="id"
            size="small"
            columns={prescriptionColumns}
            dataSource={prescriptions}
            loading={loadingPrescriptions}
            pagination={{ pageSize: 5, showSizeChanger: false }}
            scroll={{ x: 620 }}
            locale={{
              emptyText: (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="该患者暂无处方记录"
                  style={{ padding: '16px 0' }}
                />
              ),
            }}
          />
        </>
      )}
    </Drawer>
  );
}
