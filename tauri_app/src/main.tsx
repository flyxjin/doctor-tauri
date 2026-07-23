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
      // 搜索关键字切换时保留上一次数据，避免表格闪烁加载态
      placeholderData: (prev: unknown) => prev,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
