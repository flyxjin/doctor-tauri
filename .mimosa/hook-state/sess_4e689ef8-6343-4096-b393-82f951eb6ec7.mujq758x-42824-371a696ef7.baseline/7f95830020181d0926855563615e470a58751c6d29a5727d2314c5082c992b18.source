// 查询错误 Alert：统一的错误展示 + 重试按钮
//
// 替换各页面中重复的 {isError && <Alert .../>} 模式，
// 暴露 refetch 给用户，避免刷新整页才能重试。

import { Alert, Button } from 'antd';
import { formatError } from '@/utils/formatError';

interface QueryErrorAlertProps {
  /** 错误对象（来自 useQuery 的 error） */
  error: unknown;
  /** 重试回调（来自 useQuery 的 refetch） */
  onRetry?: () => void;
  /** 自定义标题，默认"加载数据失败" */
  message?: string;
  /** 重试按钮是否处于 loading 态 */
  retrying?: boolean;
}

export default function QueryErrorAlert({
  error,
  onRetry,
  message = '加载数据失败',
  retrying = false,
}: QueryErrorAlertProps) {
  return (
    <Alert
      type="error"
      showIcon
      message={message}
      description={formatError(error)}
      style={{ marginBottom: 16 }}
      action={
        onRetry ? (
          <Button size="small" onClick={onRetry} loading={retrying}>
            重试
          </Button>
        ) : undefined
      }
    />
  );
}
