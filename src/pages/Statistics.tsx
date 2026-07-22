import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Alert,
  Button,
  DatePicker,
  Space,
  Table,
  Tag,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import { getStatistics } from '@/api/tauri';
import type { DailyTrend, TopMedicine } from '@/types';
import StatCard from '@/components/StatCard';
import EmptyState from '@/components/EmptyState';

const { RangePicker } = DatePicker;

export default function StatisticsPage() {
  const [range, setRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(29, 'day'),
    dayjs(),
  ]);

  const startDate = range[0].format('YYYY-MM-DD');
  const endDate = range[1].format('YYYY-MM-DD');

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['statistics', startDate, endDate],
    queryFn: () => getStatistics(startDate, endDate),
  });

  const quickRange = (days: number) => {
    setRange([dayjs().subtract(days - 1, 'day'), dayjs()]);
  };

  const topColumns: ColumnsType<TopMedicine> = [
    {
      title: '排名',
      key: 'rank',
      width: 70,
      render: (_v, _r, i) => {
        const color = i < 3 ? ['#dc2626', '#ea580c', '#d97706'][i] : '#6b7280';
        return <Tag color={color}>{i + 1}</Tag>;
      },
    },
    { title: '药材', dataIndex: 'medicine_name', key: 'medicine_name' },
    {
      title: '销售数量',
      dataIndex: 'total_quantity',
      key: 'total_quantity',
      align: 'right',
      render: (q: number) => q.toFixed(0),
    },
    {
      title: '销售金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      align: 'right',
      render: (a: number) => `¥${a.toFixed(2)}`,
    },
  ];

  const trendColumns: ColumnsType<DailyTrend> = [
    { title: '日期', dataIndex: 'date', key: 'date', width: 140 },
    {
      title: '处方数',
      dataIndex: 'prescription_count',
      key: 'prescription_count',
      align: 'right',
    },
    {
      title: '销售额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      align: 'right',
      render: (a: number) => `¥${a.toFixed(2)}`,
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">销售统计</h1>
        <p className="page-subtitle">按时间范围统计销售情况、热销药材与每日趋势</p>
      </div>

      <Space style={{ marginBottom: 16 }} wrap>
        <RangePicker
          value={range}
          onChange={(v) => {
            if (v && v[0] && v[1]) setRange([v[0], v[1]]);
          }}
        />
        <Button onClick={() => quickRange(7)}>近 7 天</Button>
        <Button onClick={() => quickRange(30)}>近 30 天</Button>
        <Button onClick={() => quickRange(90)}>近 90 天</Button>
      </Space>

      {isError && (
        <Alert
          type="error"
          showIcon
          message="加载统计数据失败"
          description={String(error)}
          style={{ marginBottom: 16 }}
        />
      )}

      <div className="stat-grid">
        <StatCard
          title="处方数"
          value={data?.summary.prescription_count ?? 0}
          loading={isLoading}
        />
        <StatCard
          title="销售总额"
          value={data?.summary.total_amount ?? 0}
          precision={2}
          prefix="¥"
          loading={isLoading}
          variant="accent"
        />
        <StatCard
          title="涉及药材味数"
          value={data?.summary.medicine_kinds ?? 0}
          loading={isLoading}
          variant="success"
        />
        <StatCard
          title="客单价"
          value={data?.summary.avg_amount ?? 0}
          precision={2}
          prefix="¥"
          loading={isLoading}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="table-card">
          <div className="table-title">热销药材 TOP 10</div>
          <Table<TopMedicine>
            rowKey="medicine_name"
            size="small"
            loading={isLoading}
            columns={topColumns}
            dataSource={data?.top_medicines ?? []}
            pagination={false}
            locale={{
              emptyText: (
                <EmptyState
                  title="区间内无销售记录"
                  description="调整时间范围或确认是否已开具处方"
                />
              ),
            }}
          />
        </div>
        <div className="table-card">
          <div className="table-title">每日销售趋势</div>
          <Table<DailyTrend>
            rowKey="date"
            size="small"
            loading={isLoading}
            columns={trendColumns}
            dataSource={data?.daily_trend ?? []}
            pagination={{ pageSize: 10, showSizeChanger: false }}
            locale={{
              emptyText: (
                <EmptyState
                  title="区间内无销售记录"
                  description="调整时间范围或确认是否已开具处方"
                />
              ),
            }}
          />
        </div>
      </div>
    </div>
  );
}
