import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Button, Result } from 'antd';

interface ErrorBoundaryProps {
  /** 子组件树 */
  children: ReactNode;
}

interface ErrorBoundaryState {
  /** 捕获到的错误；为 null 表示无错误 */
  error: Error | null;
}

/**
 * 错误边界组件。
 *
 * 捕获子组件渲染过程中的 JavaScript 错误，显示友好的红色主题错误提示，
 * 并提供「重试」按钮以重置错误状态、重新渲染子组件树。
 *
 * 基于 React 类组件的 `componentDidCatch` 生命周期实现。
 * 注意：错误边界不会捕获事件回调、异步代码、SSR 错误。
 *
 * 调用示例：
 * ```tsx
 * <ErrorBoundary>
 *   <App />
 * </ErrorBoundary>
 * ```
 */
export default class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // 错误已上报到 state；此处可扩展上报到日志服务
    console.error('ErrorBoundary 捕获到渲染错误:', error, info);
  }

  /** 重置错误状态，触发子组件树重新渲染 */
  handleRetry = (): void => {
    this.setState({ error: null });
  };

  render(): ReactNode {
    if (this.state.error) {
      return (
        <Result
          status="error"
          title="页面渲染出错"
          subTitle={
            this.state.error.message ||
            '抱歉，页面在渲染过程中发生未知错误。'
          }
          extra={[
            <Button key="retry" type="primary" onClick={this.handleRetry}>
              重试
            </Button>,
          ]}
          style={{ padding: '48px 24px' }}
        >
          {import.meta.env.DEV && this.state.error.stack && (
            <pre
              style={{
                textAlign: 'left',
                background: '#fef2f2',
                color: '#991b1b',
                padding: 12,
                borderRadius: 6,
                fontSize: 12,
                maxHeight: 240,
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
              }}
            >
              {this.state.error.stack}
            </pre>
          )}
        </Result>
      );
    }
    return this.props.children;
  }
}
