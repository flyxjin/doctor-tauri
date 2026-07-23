import { useEffect, useMemo, useState } from 'react';
import { App, Layout, Menu, Tag, Typography, Spin } from 'antd';
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
import { checkAndDownloadSilently, installUpdate } from '@/api/tauri';
import { formatFileSize } from '@/utils/format';

const { Header, Sider, Content } = Layout;
const { Paragraph, Text } = Typography;

/** 当前应用版本（与 Cargo.toml / tauri.conf.json 对齐） */
const CURRENT_VERSION = '0.3.2';

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
  const { message, modal } = App.useApp();
  const [installing, setInstalling] = useState(false);

  // 启动时静默检查更新：仅触发一次，失败不提示
  useEffect(() => {
    let cancelled = false;
    // 延迟 1.5s，避免与首屏数据请求争抢网络
    const timer = setTimeout(() => {
      checkAndDownloadSilently(CURRENT_VERSION)
        .then((result) => {
          if (cancelled) return;
          if (!result.has_update) return;
          const info = result.info;
          if (result.downloaded_path) {
            // 已下载完成：弹窗询问是否立即静默安装
            modal.confirm({
              title: '发现新版本，已下载完成',
              width: 520,
              content: (
                <div>
                  <Paragraph>
                    <Text strong>新版本：</Text>
                    <Tag color="blue">v{info.version}</Tag>
                    <Text type="secondary" style={{ marginLeft: 8 }}>
                      当前 v{CURRENT_VERSION}
                    </Text>
                  </Paragraph>
                  {info.file_size > 0 && (
                    <Paragraph type="secondary" style={{ marginBottom: 8 }}>
                      安装包大小：{formatFileSize(info.file_size)}
                    </Paragraph>
                  )}
                  <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                    点击「立即更新」将自动静默安装并重启应用，期间请勿关闭程序。
                  </Paragraph>
                </div>
              ),
              okText: '立即更新',
              cancelText: '稍后',
              onOk: async () => {
                setInstalling(true);
                try {
                  await installUpdate(result.downloaded_path, true);
                  // 静默安装已启动，后端会在 500ms 后调用 app.exit(0)
                  message.info('正在静默安装并退出，请稍候...');
                } catch (e) {
                  setInstalling(false);
                  message.error(`启动安装失败：${String(e)}`);
                }
              },
            });
          } else {
            // 有新版本但下载失败：仅提示用户到 Settings 页手动操作
            message.info(
              `发现新版本 v${info.version}，自动下载失败，请到「系统设置」手动下载`,
              6,
            );
          }
        })
        .catch(() => {
          // 静默失败：不干扰用户启动
        });
    }, 1500);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

      {/* 静默安装中遮罩：后端 spawn 安装程序后约 500ms 调用 app.exit(0) */}
      {installing && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.45)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            color: '#fff',
          }}
        >
          <Spin size="large" />
          <div style={{ marginTop: 16, fontSize: 15 }}>正在静默安装新版本并退出...</div>
          <div style={{ marginTop: 4, fontSize: 12, opacity: 0.7 }}>请勿关闭程序</div>
        </div>
      )}
    </Layout>
  );
}
