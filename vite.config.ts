import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// Tauri 期望固定的端口与外部可达的 host
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // Tauri 要求在开发时通过环境变量指定端口
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    host: '0.0.0.0',
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 1421,
    },
    watch: {
      // 不监听 Rust 后端目录，避免不必要的重启
      ignored: ['**/src-tauri/**'],
    },
  },
  // Tauri 使用相对路径加载资源
  base: './',
  build: {
    // WebView2 为常青 Chromium，ES2022 全量支持
    target: 'es2022',
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        // 第三方库分包：避免单个 chunk 过大
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'antd-vendor': ['antd'],
          'icons-vendor': ['@ant-design/icons'],
          'query-vendor': ['@tanstack/react-query'],
          // dayjs 独立分包，长期稳定无需随业务 chunk 变化失效缓存
          'date-vendor': ['dayjs'],
        },
      },
    },
    // 分包后单 chunk 上限放宽
    chunkSizeWarningLimit: 600,
  },
});
