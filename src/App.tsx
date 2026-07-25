import { lazy, Suspense } from 'react';
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ConfigProvider, App as AntdApp, Spin } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from '@/layouts/MainLayout';
import ErrorBoundary from '@/components/ErrorBoundary';

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

/** 东方本草主题：深草本绿 + 朱砂点缀
 *
 * 提升到模块顶层作为常量，避免 App 每次渲染都重建对象引用，
 * 减少 ConfigProvider 不必要的主题重计算。
 */
const theme = {
  token: {
    colorPrimary: '#2D5F3F',
    colorSuccess: '#5B8C3E',
    colorWarning: '#D4943A',
    colorError: '#B83A2E',
    colorInfo: '#2D5F3F',
    borderRadius: 8,
    fontSize: 14,
    colorBgLayout: '#F7F4EF',
    colorBorder: '#E5DFD5',
    colorText: '#1A1A1A',
    colorTextSecondary: '#4A4A4A',
    fontFamily: "'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif",
  },
  components: {
    Layout: {
      siderBg: '#1F4530',
      headerBg: '#FDFAF5',
      headerHeight: 56,
      bodyBg: '#F7F4EF',
    },
    Menu: {
      darkItemBg: '#1F4530',
      darkItemSelectedBg: 'rgba(200, 71, 44, 0.25)',
      darkItemColor: 'rgba(232, 240, 234, 0.65)',
      darkItemSelectedColor: '#FDFAF5',
      darkItemHoverBg: 'rgba(255, 255, 255, 0.06)',
      itemHeight: 40,
      itemMarginInline: 0,
    },
    Table: {
      headerBg: '#F7F4EF',
      headerColor: '#4A4A4A',
      rowHoverBg: '#E8F0EA',
      borderColor: '#F0EBE0',
    },
    Card: {
      borderRadiusLG: 12,
      colorBorderSecondary: '#F0EBE0',
    },
    Statistic: {
      contentFontSize: 32,
    },
  },
};

function App() {
  return (
    <ConfigProvider locale={zhCN} theme={theme}>
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

export default App;
