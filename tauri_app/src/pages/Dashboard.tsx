import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Space, Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  DatabaseOutlined,
  FileTextOutlined,
  MedicineBoxOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getDashboardData } from '@/api/tauri';
import type { LowStockItem, Prescription } from '@/types';
import StatCard from '@/components/StatCard';
import EmptyState from '@/components/EmptyState';

export default function Dashboard() {
  const navigate = useNavigate();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardData,
  });

  const lowStockColumns: ColumnsType<LowStockItem> = [
    { title: '药材', dataIndex: 'medicine_name', key: 'medicine_name' },
    {
      title: '当前库存',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (q: number, r) => (
        <span className="low-stock-tag">
          {q} {r.unit}
        </span>
      ),
    },
    { title: '最低库存', dataIndex: 'min_stock', key: 'min_stock' },
    {
      title: '',
      key: 'action',
      width: 90,
      render: () => (
        <Button
          type="link"
          size="small"
          onClick={() => navigate('/inventory')}
        >
          去入库
        </Button>
      ),
    },
  ];

  const recentColumns: ColumnsType<Prescription> = [
    { title: '处方号', dataIndex: 'id', key: 'id', width: 80 },
    { title: '患者', dataIndex: 'patient_name', key: 'patient_name' },
    { title: '性别', dataIndex: 'patient_gender', key: 'patient_gender', width: 80 },
    { title: '诊断', dataIndex: 'diagnosis', key: 'diagnosis', ellipsis: true },
    {
      title: '金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      align: 'right',
      render: (v: number) => `¥${v.toFixed(2)}`,
    },
    { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">首页概览</h1>
        <p className="page-subtitle">系统关键指标与待办事项一览</p>
      </div>

      {isError && (
        <Alert
          type="error"
          showIcon
          message="加载看板数据失败"
          description={String(error)}
          style={{ marginBottom: 16 }}
        />
      )}

      <div className="stat-grid">
        <StatCard
          title="药材种类"
          value={data?.medicine_count ?? 0}
          loading={isLoading}
          variant="success"
        />
        <StatCard
          title="处方总数"
          value={data?.prescription_count ?? 0}
          loading={isLoading}
        />
        <StatCard
          title="库存总值"
          value={data?.total_stock_value ?? 0}
          precision={2}
          prefix="¥"
          loading={isLoading}
          variant="accent"
        />
        <StatCard
          title="低库存预警"
          value={data?.low_stock_count ?? 0}
          loading={isLoading}
          variant={data && data.low_stock_count > 0 ? 'warning' : 'default'}
        />
      </div>

      {/* 快捷操作入口 */}
      <div className="quick-actions">
        <div className="quick-actions-title">快捷操作</div>
        <Space size={[12, 12]} wrap>
          <Button
            type="primary"
            size="large"
            icon={<FileTextOutlined />}
            onClick={() => navigate('/prescription')}
          >
            开处方
          </Button>
          <Button
            size="large"
            icon={<PlusOutlined />}
            onClick={() => navigate('/medicines')}
          >
            新增药材
          </Button>
          <Button
            size="large"
            icon={<DatabaseOutlined />}
            onClick={() => navigate('/inventory')}
          >
            库存管理
          </Button>
          <Button
            size="large"
            icon={<MedicineBoxOutlined />}
            onClick={() => navigate('/batch-import')}
          >
            批量导入
          </Button>
        </Space>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="table-card">
          <div className="table-title">
            低库存预警
            {data && data.low_stock_count > 0 && (
              <Tag color="orange" style={{ marginLeft: 8 }}>
                {data.low_stock_count} 种
              </Tag>
            )}
          </div>
          <Table<LowStockItem>
            rowKey="medicine_id"
            size="small"
            loading={isLoading}
            columns={lowStockColumns}
            dataSource={data?.low_stock_list ?? []}
            pagination={false}
            locale={{
              emptyText: <EmptyState title="库存充足" description="当前无低库存预警药材" />,
            }}
          />
        </div>
        <div className="table-card">
          <div className="table-title">
            最近处方
            <Button
              type="link"
              size="small"
              style={{ marginLeft: 'auto' }}
              onClick={() => navigate('/history')}
            >
              查看全部
            </Button>
          </div>
          <Table<Prescription>
            rowKey="id"
            size="small"
            loading={isLoading}
            columns={recentColumns}
            dataSource={data?.recent_prescriptions ?? []}
            pagination={false}
            onRow={(record) => ({
              onDoubleClick: () => navigate('/history', { state: { focusId: record.id } }),
              style: { cursor: 'pointer' },
            })}
            locale={{
              emptyText: <EmptyState title="暂无处方" description="系统启动后开方记录将显示在此处" />,
            }}
          />
        </div>
      </div>
    </div>
  );
}
