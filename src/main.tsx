import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './styles/global.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // 避免频繁重复请求
      staleTime: 30 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
      // 注意：不设全局 placeholderData —— 按实体 id/名称切换的查询（患者详情、
      // 药材历史、统计日期区间）若沿用旧数据，会把上一个实体的数据短暂展示在
      // 新实体名下，误导用户。需要"搜索关键字切换不闪烁"的列表页
      // 显式使用 placeholderData: keepPreviousData（History/MedicineList/Patients）。
    },
  },
});

// 浏览器演示模式：普通浏览器打开 dev server 时拦截 invoke 返回演示数据。
// Tauri 窗口内存在 __TAURI_INTERNALS__，永远不会走到这里。
async function prepare() {
  if (import.meta.env.DEV && !('__TAURI_INTERNALS__' in window)) {
    const { installTauriMock } = await import('./mocks/tauriMock');
    installTauriMock();
  }
}

void prepare().finally(() => {
  ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </React.StrictMode>,
  );
});
