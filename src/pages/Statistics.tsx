import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  App,
  Button,
  DatePicker,
  Space,
  Table,
  Tag,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { ExportOutlined } from '@ant-design/icons';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';

dayjs.locale('zh-cn');

/** 快捷时间范围定义 */
type QuickKey = 'today' | 'week' | 'month' | 'quarter' | 'year' | 'all';
const QUICK_RANGES: { label: string; key: QuickKey }[] = [
  { label: '今日', key: 'today' },
  { label: '本周', key: 'week' },
  { label: '本月', key: 'month' },
  { label: '本季', key: 'quarter' },
  { label: '本年', key: 'year' },
  { label: '全部', key: 'all' },
];

/** 根据快捷 key 计算日期范围 */
function getQuickRange(key: QuickKey): [Dayjs, Dayjs] {
  const today = dayjs();
  switch (key) {
    case 'today':
      return [today.startOf('day'), today.endOf('day')];
    case 'week':
      return [today.startOf('week'), today.endOf('day')];
    case 'month':
      return [today.startOf('month'), today.endOf('day')];
    case 'quarter': {
      const qMonth = Math.floor(today.month() / 3) * 3;
      return [today.month(qMonth).startOf('month'), today.endOf('day')];
    }
    case 'year':
      return [today.startOf('year'), today.endOf('day')];
    case 'all':
      return [dayjs('2020-01-01'), today.endOf('day')];
  }
}
import { getDoctorStats, getStatistics } from '@/api/tauri';
import type { DailyTrend, DoctorStat, TopMedicine } from '@/types';
import StatCard from '@/components/StatCard';
import EmptyState from '@/components/EmptyState';
import TrendChart from '@/components/TrendChart';
import QueryErrorAlert from '@/components/QueryErrorAlert';
import { useCsvExport } from '@/hooks/useCsvExport';

const { RangePicker } = DatePicker;

export default function StatisticsPage() {
  const { message } = App.useApp();
  // 初始范围与快捷选中态保持一致（默认「本月」），避免高亮与实际区间不匹配
  const [range, setRange] = useState<[Dayjs, Dayjs]>(() => getQuickRange('month'));
  // 当前快捷范围选中态：null 表示用户自定义了 RangePicker
  const [quickSelected, setQuickSelected] = useState<QuickKey | null>('month');

  // CSV 导出：复用统一 hook
  const { exportCsv } = useCsvExport({ filenamePrefix: 'statistics', label: '统计报表' });

  const startDate = range[0].format('YYYY-MM-DD');
  const endDate = range[1].format('YYYY-MM-DD');

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['statistics', startDate, endDate],
    queryFn: () => getStatistics(startDate, endDate),
    staleTime: 2 * 60 * 1000,
  });

  // 医师开方量：按开方人聚合（与上方统计共用日期区间）
  const { data: doctorStats, isLoading: doctorStatsLoading } = useQuery({
    queryKey: ['doctor-stats', startDate, endDate],
    queryFn: () => getDoctorStats(startDate, endDate),
    staleTime: 2 * 60 * 1000,
  });

  const doctorColumns: ColumnsType<DoctorStat> = [
    { title: '医师', dataIndex: 'created_by', key: 'created_by' },
    {
      title: '处方数',
      dataIndex: 'prescription_count',
      key: 'prescription_count',
      width: 100,
      align: 'right',
      render: (v: number) => <Tag color="blue">{v}</Tag>,
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 120,
      align: 'right',
      render: (v: number) => `¥${v.toFixed(2)}`,
    },
  ];

  const handleQuickRange = (key: QuickKey) => {
    setRange(getQuickRange(key));
    setQuickSelected(key);
  };

  const handleRangePickerChange = (v: [Dayjs, Dayjs] | null) => {
    if (v && v[0] && v[1]) {
      setRange([v[0], v[1]]);
      setQuickSelected(null);
    }
  };

  // 导出每日销售趋势 CSV（含汇总信息头 + 趋势明细 + 热销药材）
  const handleExportCsv = async () => {
    const trend = data?.daily_trend ?? [];
    const top = data?.top_medicines ?? [];
    if (trend.length === 0 && top.length === 0) {
      message.warning('没有可导出的数据');
      return;
    }
    const rows: (string | number | null | undefined)[][] = [];
    // 汇总信息头
    rows.push(['中药材销售统计报表']);
    rows.push([`统计区间：${startDate} 至 ${endDate}`]);
    rows.push([
      `处方数：${data?.summary.prescription_count ?? 0}`,
      `销售总额：${(data?.summary.total_amount ?? 0).toFixed(2)}`,
      `涉及药材味数：${data?.summary.medicine_kinds ?? 0}`,
      `客单价：${(data?.summary.avg_amount ?? 0).toFixed(2)}`,
    ]);
    rows.push([]);
    // 每日趋势明细
    rows.push(['【每日销售趋势】']);
    rows.push(['日期', '处方数', '销售额']);
    for (const t of trend) {
      rows.push([t.date, t.prescription_count, t.total_amount.toFixed(2)]);
    }
    rows.push([]);
    // 热销药材 TOP 10
    rows.push(['【热销药材 TOP 10】']);
    rows.push(['排名', '药材', '销售数量', '销售金额']);
    top.forEach((m, i) => {
      rows.push([i + 1, m.medicine_name, m.total_quantity.toFixed(0), m.total_amount.toFixed(2)]);
    });
    await exportCsv(rows);
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
          onChange={(v) => handleRangePickerChange(v as [Dayjs, Dayjs] | null)}
        />
        {QUICK_RANGES.map((r) => (
          <Button
            key={r.key}
            type={quickSelected === r.key ? 'primary' : 'default'}
            onClick={() => handleQuickRange(r.key)}
          >
            {r.label}
          </Button>
        ))}
        <Button
          icon={<ExportOutlined />}
          onClick={handleExportCsv}
          disabled={!data || (data.daily_trend.length === 0 && data.top_medicines.length === 0)}
        >
          导出 CSV
        </Button>
      </Space>

      {isError && (
        <QueryErrorAlert
          error={error}
          onRetry={refetch}
          retrying={isFetching}
          message="加载统计数据失败"
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
          {!isLoading && (data?.daily_trend ?? []).length > 0 ? (
            <div style={{ marginBottom: 16 }}>
              <TrendChart<DailyTrend>
                data={data!.daily_trend}
                xKey="date"
                height={260}
                lines={[
                  // 使用 CSS 变量，浅色/深色主题下自动适配
                  { key: 'total_amount', name: '销售额', color: 'var(--accent-color)' },
                  { key: 'prescription_count', name: '处方数', color: 'var(--primary-color)', area: false },
                ]}
              />
            </div>
          ) : null}
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

      <div className="table-card" style={{ marginTop: 16 }}>
        <div className="table-title">医师开方量 TOP 20</div>
        <Table<DoctorStat>
          rowKey="created_by"
          size="small"
          loading={doctorStatsLoading}
          columns={doctorColumns}
          dataSource={doctorStats ?? []}
          pagination={false}
          locale={{
            emptyText: (
              <EmptyState
                title="区间内无开方记录"
                description="调整时间范围或确认是否已开具处方"
              />
            ),
          }}
        />
      </div>
    </div>
  );
}
