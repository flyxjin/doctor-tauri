import { useQuery } from '@tanstack/react-query';
import { Button, Space, Table, Tag, Tooltip } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  DatabaseOutlined,
  FileTextOutlined,
  MedicineBoxOutlined,
  PlusOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getDashboardData } from '@/api/tauri';
import type { DashboardDailyTrend, LowStockItem, Prescription } from '@/types';
import StatCard from '@/components/StatCard';
import EmptyState from '@/components/EmptyState';
import TrendChart from '@/components/TrendChart';
import QueryErrorAlert from '@/components/QueryErrorAlert';

export default function Dashboard() {
  const navigate = useNavigate();
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardData,
    staleTime: 30 * 1000,
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
      <div className="page-header-flex">
        <div className="page-header">
          <h1 className="page-title">首页概览</h1>
          <p className="page-subtitle">系统关键指标与待办事项一览</p>
        </div>
        <Tooltip title="手动刷新看板数据">
          <Button
            icon={<ReloadOutlined spin={isFetching} />}
            onClick={() => refetch()}
            loading={isFetching && !isLoading}
          >
            刷新
          </Button>
        </Tooltip>
      </div>

      {isError && (
        <QueryErrorAlert
          error={error}
          onRetry={refetch}
          retrying={isFetching}
          message="加载看板数据失败"
        />
      )}

      {/* 今日概览：突出展示当日业绩 */}
      <div className="today-banner">
        <div className="today-banner-label">今日概览</div>
        <div className="today-banner-stats">
          <div className="today-banner-item">
            <span className="today-banner-num">
              {data?.today_prescription_count ?? 0}
            </span>
            <span className="today-banner-unit">张处方</span>
          </div>
          <div className="today-banner-divider" />
          <div className="today-banner-item">
            <span className="today-banner-num">
              ¥{(data?.today_revenue ?? 0).toFixed(2)}
            </span>
            <span className="today-banner-unit">销售收入</span>
          </div>
        </div>
      </div>

      <div className="stat-grid">
        {/* Tooltip 需包裹普通元素以承接 ref，StatCard 非 forwardRef 组件 */}
        <Tooltip title="点击查看药材管理">
          <div>
            <StatCard
              title="药材种类"
              value={data?.medicine_count ?? 0}
              loading={isLoading}
              variant="success"
              onClick={() => navigate('/medicines')}
            />
          </div>
        </Tooltip>
        <Tooltip title="点击查看处方历史">
          <div>
            <StatCard
              title="处方总数"
              value={data?.prescription_count ?? 0}
              loading={isLoading}
              onClick={() => navigate('/history')}
            />
          </div>
        </Tooltip>
        <Tooltip title="点击查看库存管理">
          <div>
            <StatCard
              title="库存总值"
              value={data?.total_stock_value ?? 0}
              precision={2}
              prefix="¥"
              loading={isLoading}
              variant="accent"
              onClick={() => navigate('/inventory')}
            />
          </div>
        </Tooltip>
        <Tooltip title="点击查看库存管理">
          <div>
            <StatCard
              title="低库存预警"
              value={data?.low_stock_count ?? 0}
              loading={isLoading}
              variant={data && data.low_stock_count > 0 ? 'warning' : 'default'}
              onClick={() => navigate('/inventory')}
            />
          </div>
        </Tooltip>
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

      {/* 近 7 天营收趋势 */}
      {data && data.daily_trend && data.daily_trend.length > 0 && (
        <div className="table-card" style={{ marginBottom: 16 }}>
          <div className="table-title">近 7 天营收趋势</div>
          <TrendChart<DashboardDailyTrend>
            data={data.daily_trend}
            xKey="date"
            height={240}
            lines={[
              // 使用 CSS 变量，浅色/深色主题下自动适配
              { key: 'revenue', name: '营收', color: 'var(--accent-color)' },
              { key: 'prescription_count', name: '处方数', color: 'var(--primary-color)', area: false },
            ]}
          />
        </div>
      )}

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
