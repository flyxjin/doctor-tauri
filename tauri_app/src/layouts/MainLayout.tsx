import { useMemo } from 'react';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  MedicineBoxOutlined,
  FileTextOutlined,
  TeamOutlined,
  DatabaseOutlined,
  HistoryOutlined,
  BarChartOutlined,
  ImportOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { Link, Outlet, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

/** 侧边栏导航项 */
const NAV_ITEMS = [
  { key: '/', icon: <DashboardOutlined />, label: '首页概览' },
  { key: '/medicines', icon: <MedicineBoxOutlined />, label: '药材管理' },
  { key: '/prescription', icon: <FileTextOutlined />, label: '开处方' },
  { key: '/patients', icon: <TeamOutlined />, label: '客户管理' },
  { key: '/inventory', icon: <DatabaseOutlined />, label: '库存管理' },
  { key: '/history', icon: <HistoryOutlined />, label: '处方历史' },
  { key: '/statistics', icon: <BarChartOutlined />, label: '销售统计' },
  { key: '/batch-import', icon: <ImportOutlined />, label: '批量导入' },
  { key: '/settings', icon: <SettingOutlined />, label: '系统设置' },
];

/** 格式化当前日期 */
function formatToday(): string {
  const now = new Date();
  const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 星期${weekdays[now.getDay()]}`;
}

export default function MainLayout() {
  const location = useLocation();

  const selectedKey = useMemo(() => {
    const path = location.pathname;
    const matched = NAV_ITEMS.filter(
      (item) => path === item.key || (item.key !== '/' && path.startsWith(item.key)),
    );
    return matched.length > 0 ? matched[matched.length - 1].key : '/';
  }, [location.pathname]);

  const menuItems = NAV_ITEMS.map((item) => ({
    key: item.key,
    icon: item.icon,
    label: <Link to={item.key}>{item.label}</Link>,
  }));

  const currentLabel = NAV_ITEMS.find((item) => item.key === selectedKey)?.label ?? '首页概览';

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={208} theme="dark" className="tcm-sider">
        <div className="tcm-logo">
          <div className="tcm-logo-icon">本</div>
          <div className="tcm-logo-text">
            中药材
            <br />
            销售管理系统
          </div>
        </div>
        <Menu
          mode="inline"
          theme="dark"
          selectedKeys={[selectedKey]}
          items={menuItems}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header className="tcm-header">
          <span className="tcm-header-title">{currentLabel}</span>
          <span className="tcm-header-date">{formatToday()}</span>
        </Header>
        <Content style={{ overflow: 'auto' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
