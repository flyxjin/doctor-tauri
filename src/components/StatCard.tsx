import { Skeleton } from 'antd';

export interface StatCardProps {
  title: string;
  value: number | string;
  precision?: number;
  prefix?: string;
  suffix?: string;
  variant?: 'default' | 'accent' | 'success' | 'warning';
  loading?: boolean;
}

/** 东方本草风格统计卡片 */
export default function StatCard({
  title,
  value,
  precision,
  prefix,
  suffix,
  variant = 'default',
  loading,
}: StatCardProps) {
  const variantClass = variant !== 'default' ? ` ${variant}` : '';

  const formatValue = () => {
    if (typeof value === 'string') return value;
    const num = precision != null ? value.toFixed(precision) : value.toLocaleString('zh-CN');
    return num;
  };

  return (
    <div className={`tcm-stat-card${variantClass}`}>
      {loading ? (
        <Skeleton active paragraph={{ rows: 1, width: '60%' }} title={{ width: '40%' }} />
      ) : (
        <>
          <div className="stat-label">{title}</div>
          <div className="stat-value">
            {prefix && <span className="stat-prefix">{prefix}</span>}
            {formatValue()}
            {suffix && <span className="stat-prefix">{suffix}</span>}
          </div>
        </>
      )}
    </div>
  );
}
