import { Card, Spin } from 'antd';

export interface LoadingCardProps {
  /** 卡片标题（显示在 Card.title 位置） */
  title: string;
  /** 卡片高度，默认 200 */
  height?: number;
}

/**
 * 加载中卡片组件。
 *
 * 基于 AntD `Spin` + `Card` 组合，居中显示加载动画。
 * 适用于：
 * - 异步数据首次加载
 * - 区块占位等待后端响应
 *
 * 调用示例：
 * ```tsx
 * {isLoading && <LoadingCard title="药材列表" height={300} />}
 * ```
 */
export default function LoadingCard({
  title,
  height = 200,
}: LoadingCardProps) {
  return (
    <Card title={title} bordered={false} style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height,
        }}
      >
        <Spin tip="加载中..." size="large">
          <div style={{ padding: 24, minHeight: height }} />
        </Spin>
      </div>
    </Card>
  );
}
