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
import { getStatistics, saveTextToDownloads } from '@/api/tauri';
import type { DailyTrend, TopMedicine } from '@/types';
import StatCard from '@/components/StatCard';
import EmptyState from '@/components/EmptyState';
import TrendChart from '@/components/TrendChart';
import QueryErrorAlert from '@/components/QueryErrorAlert';
import { rowsToCsv } from '@/utils/csv';
import { formatError } from '@/utils/formatError';

const { RangePicker } = DatePicker;

export default function StatisticsPage() {
  const { message } = App.useApp();
  const [range, setRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(29, 'day'),
    dayjs(),
  ]);
  // 当前快捷范围选中态：null 表示用户自定义了 RangePicker
  const [quickSelected, setQuickSelected] = useState<number | null>(30);

  const startDate = range[0].format('YYYY-MM-DD');
  const endDate = range[1].format('YYYY-MM-DD');

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['statistics', startDate, endDate],
    queryFn: () => getStatistics(startDate, endDate),
    staleTime: 2 * 60 * 1000,
  });

  const quickRange = (days: number) => {
    setRange([dayjs().subtract(days - 1, 'day'), dayjs()]);
    setQuickSelected(days);
  };

  const handleRangePickerChange = (v: [Dayjs, Dayjs] | null) => {
    if (v && v[0] && v[1]) {
      setRange([v[0], v[1]]);
      // 判断是否匹配某个快捷范围（结束日期为今天）
      const today = dayjs().startOf('day');
      if (v[1].startOf('day').isSame(today)) {
        const diff = v[0].startOf('day').diff(today, 'day') * -1 + 1;
        if ([7, 30, 90].includes(diff)) {
          setQuickSelected(diff);
          return;
        }
      }
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
    const csv = rowsToCsv(rows);
    try {
      const ts = dayjs().format('YYYYMMDD_HHmmss');
      const path = await saveTextToDownloads(`statistics_${ts}.csv`, csv);
      message.success(`已导出到：${path}`);
    } catch (e) {
      message.error(formatError(e));
    }
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
        <Button
          type={quickSelected === 7 ? 'primary' : 'default'}
          onClick={() => quickRange(7)}
        >
          近 7 天
        </Button>
        <Button
          type={quickSelected === 30 ? 'primary' : 'default'}
          onClick={() => quickRange(30)}
        >
          近 30 天
        </Button>
        <Button
          type={quickSelected === 90 ? 'primary' : 'default'}
          onClick={() => quickRange(90)}
        >
          近 90 天
        </Button>
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
                  { key: 'total_amount', name: '销售额', color: '#C8472C' },
                  { key: 'prescription_count', name: '处方数', color: '#2D5F3F', area: false },
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
    </div>
  );
}
