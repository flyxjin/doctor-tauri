import { Empty } from 'antd';
import type { ReactNode } from 'react';

export interface EmptyStateProps {
  /** 自定义图标，默认使用 AntD Empty 内置图标 */
  icon?: ReactNode;
  /** 主标题（粗体显示） */
  title: string;
  /** 副标题/描述文字（灰色辅助说明） */
  description?: string;
  /** 可选操作区域，通常放一个按钮 */
  action?: ReactNode;
}

/**
 * 通用空状态组件。
 *
 * 基于 AntD `Empty`，统一东方本草主题色调，用于：
 * - 表格无数据
 * - 搜索无结果
 * - 列表为空
 *
 * 调用示例：
 * ```tsx
 * <EmptyState title="暂无处方" description="点击「开方」按钮新建处方" action={<Button>开方</Button>} />
 * ```
 */
export default function EmptyState({
  icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <Empty
      image={icon ?? Empty.PRESENTED_IMAGE_SIMPLE}
      imageStyle={{ height: 60 }}
      style={{ padding: '24px 0' }}
      description={
        <div>
          <div style={{ color: '#1A1A1A', fontWeight: 500, fontSize: 14 }}>{title}</div>
          {description && (
            <div style={{ color: '#8B8580', fontSize: 13, marginTop: 4 }}>
              {description}
            </div>
          )}
        </div>
      }
    >
      {action && <div style={{ marginTop: 12 }}>{action}</div>}
    </Empty>
  );
}
