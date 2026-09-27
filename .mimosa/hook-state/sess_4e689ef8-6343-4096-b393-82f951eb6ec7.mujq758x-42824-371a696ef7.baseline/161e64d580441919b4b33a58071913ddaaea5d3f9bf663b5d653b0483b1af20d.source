import { Skeleton } from 'antd';

export interface StatCardProps {
  title: string;
  value: number | string;
  precision?: number;
  prefix?: string;
  suffix?: string;
  variant?: 'default' | 'accent' | 'success' | 'warning';
  loading?: boolean;
  /** 点击回调；传入后卡片变为可点击样式（用于跳转关联页面） */
  onClick?: () => void;
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
  onClick,
}: StatCardProps) {
  const variantClass = variant !== 'default' ? ` ${variant}` : '';
  const clickableClass = onClick ? ' clickable' : '';

  const formatValue = () => {
    if (typeof value === 'string') return value;
    const num = precision != null ? value.toFixed(precision) : value.toLocaleString('zh-CN');
    return num;
  };

  return (
    <div
      className={`tcm-stat-card${variantClass}${clickableClass}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              // 键盘可达性：Enter/Space 触发点击
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
    >
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
