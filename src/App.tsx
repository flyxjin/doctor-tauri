import { lazy, Suspense } from 'react';
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ConfigProvider, App as AntdApp, Spin, theme as antdTheme } from 'antd';
import type { ThemeConfig } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from '@/layouts/MainLayout';
import ErrorBoundary from '@/components/ErrorBoundary';
import { ThemeProvider, useThemeMode, type ThemeMode } from '@/theme/ThemeContext';

/** 路由懒加载：按需加载页面组件，减小首屏包体积 */
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const MedicineList = lazy(() => import('@/pages/MedicineList'));
const Prescription = lazy(() => import('@/pages/Prescription'));
const Patients = lazy(() => import('@/pages/Patients'));
const Inventory = lazy(() => import('@/pages/Inventory'));
const History = lazy(() => import('@/pages/History'));
const Statistics = lazy(() => import('@/pages/Statistics'));
const BatchImport = lazy(() => import('@/pages/BatchImport'));
const Settings = lazy(() => import('@/pages/Settings'));

/** 页面加载中占位 */
function PageLoading() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
      <Spin size="large" tip="加载中..." />
    </div>
  );
}

/** 现代工作台主题：中性灰画布 + 翡翠品牌色（草本基因延续）
 *
 * 提升到模块顶层作为常量，避免 App 每次渲染都重建对象引用，
 * 减少 ConfigProvider 不必要的主题重计算。
 */
const lightTheme: ThemeConfig = {
  token: {
    colorPrimary: '#059669',
    colorSuccess: '#16A34A',
    colorWarning: '#D97706',
    colorError: '#DC2626',
    colorInfo: '#059669',
    borderRadius: 10,
    fontSize: 14,
    colorBgLayout: '#F6F7F9',
    colorBorder: '#E2E8F0',
    colorText: '#0F172A',
    colorTextSecondary: '#475569',
    fontFamily:
      "-apple-system, 'PingFang SC', 'HarmonyOS Sans SC', 'MiSans', 'Microsoft YaHei UI', 'Segoe UI', sans-serif",
  },
  components: {
    Layout: {
      siderBg: '#FFFFFF',
      headerBg: '#FFFFFF',
      headerHeight: 56,
      bodyBg: '#F6F7F9',
    },
    Menu: {
      itemBg: 'transparent',
      itemColor: '#475569',
      itemSelectedBg: '#ECFDF5',
      itemSelectedColor: '#059669',
      itemHoverBg: '#F6F7F9',
      activeBarBorderWidth: 0,
      itemHeight: 40,
      itemMarginInline: 8,
      itemBorderRadius: 10,
    },
    Table: {
      headerBg: '#F6F7F9',
      headerColor: '#475569',
      rowHoverBg: '#ECFDF5',
      borderColor: '#F1F5F9',
    },
    Card: {
      borderRadiusLG: 14,
      colorBorderSecondary: '#F1F5F9',
    },
    Statistic: {
      contentFontSize: 32,
    },
  },
};

/** 深色主题：中性深灰蓝 + 亮翡翠品牌色，基于 antd darkAlgorithm
 * 与 global.css 中 :root[data-theme='dark'] 的 CSS 变量覆盖配套 */
const darkTheme: ThemeConfig = {
  algorithm: antdTheme.darkAlgorithm,
  token: {
    colorPrimary: '#34D399',
    colorSuccess: '#4ADE80',
    colorWarning: '#F59E0B',
    colorError: '#F87171',
    colorInfo: '#34D399',
    borderRadius: 10,
    fontSize: 14,
    colorBgLayout: '#0D1117',
    colorBorder: '#29313C',
    colorText: '#E6EDF3',
    colorTextSecondary: '#9BA8B7',
    fontFamily:
      "-apple-system, 'PingFang SC', 'HarmonyOS Sans SC', 'MiSans', 'Microsoft YaHei UI', 'Segoe UI', sans-serif",
  },
  components: {
    Layout: {
      siderBg: '#151B23',
      headerBg: '#151B23',
      headerHeight: 56,
      bodyBg: '#0D1117',
    },
    Menu: {
      itemBg: 'transparent',
      itemColor: '#9BA8B7',
      itemSelectedBg: 'rgba(52, 211, 153, 0.12)',
      itemSelectedColor: '#34D399',
      itemHoverBg: 'rgba(255, 255, 255, 0.06)',
      activeBarBorderWidth: 0,
      itemHeight: 40,
      itemMarginInline: 8,
      itemBorderRadius: 10,
    },
    Table: {
      headerBg: '#1A222C',
      headerColor: '#9BA8B7',
      rowHoverBg: 'rgba(52, 211, 153, 0.08)',
      borderColor: '#1F2731',
    },
    Card: {
      borderRadiusLG: 14,
      colorBorderSecondary: '#1F2731',
    },
    Statistic: {
      contentFontSize: 32,
    },
  },
};

/** 按模式选择主题配置（模块级常量，避免每次渲染重建） */
const THEME_BY_MODE: Record<ThemeMode, ThemeConfig> = {
  light: lightTheme,
  dark: darkTheme,
};

/** 内部应用组件：根据当前主题模式选择对应的 antd 主题配置 */
function AppInner() {
  const { mode } = useThemeMode();
  return (
    <ConfigProvider locale={zhCN} theme={THEME_BY_MODE[mode]}>
      <AntdApp>
        <HashRouter>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<MainLayout />}>
                <Route
                  index
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <Dashboard />
                    </Suspense>
                  }
                />
                <Route
                  path="medicines"
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <MedicineList />
                    </Suspense>
                  }
                />
                <Route
                  path="prescription"
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <Prescription />
                    </Suspense>
                  }
                />
                <Route
                  path="patients"
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <Patients />
                    </Suspense>
                  }
                />
                <Route
                  path="inventory"
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <Inventory />
                    </Suspense>
                  }
                />
                <Route
                  path="history"
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <History />
                    </Suspense>
                  }
                />
                <Route
                  path="statistics"
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <Statistics />
                    </Suspense>
                  }
                />
                <Route
                  path="batch-import"
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <BatchImport />
                    </Suspense>
                  }
                />
                <Route
                  path="settings"
                  element={
                    <Suspense fallback={<PageLoading />}>
                      <Settings />
                    </Suspense>
                  }
                />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </ErrorBoundary>
        </HashRouter>
      </AntdApp>
    </ConfigProvider>
  );
}

/** 根组件：ThemeProvider 包在 ConfigProvider 外层，供内部组件读取主题模式 */
function App() {
  return (
    <ThemeProvider>
      <AppInner />
    </ThemeProvider>
  );
}

export default App;
