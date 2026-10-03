// 组件测试全局垫片：在 vitest.config.ts 的 setupFiles 中注册，所有测试共用
import '@testing-library/jest-dom/vitest';
// antd v5 在 React 19 下的兼容补丁（与 main.tsx 保持一致）
import '@ant-design/v5-patch-for-react-19';

// jsdom 未实现的浏览器 API（antd Grid/Table/Modal 等依赖）
if (typeof window !== 'undefined') {
  if (!window.matchMedia) {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: (query: string): MediaQueryList =>
        ({
          // min-width 查询一律命中，模拟桌面窗口（≥1024px），使响应式列展示全量列
          matches: query.includes('min-width:'),
          media: query,
          onchange: null,
          addListener: () => {},
          removeListener: () => {},
          addEventListener: () => {},
          removeEventListener: () => {},
          dispatchEvent: () => false,
        }) as MediaQueryList,
    });
  }

  class ResizeObserverMock {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
  if (!window.ResizeObserver) {
    (window as { ResizeObserver?: unknown }).ResizeObserver = ResizeObserverMock;
  }

  if (!window.scrollTo) {
    window.scrollTo = () => {};
  }
  if (!Element.prototype.scrollTo) {
    Element.prototype.scrollTo = () => {};
  }
}
