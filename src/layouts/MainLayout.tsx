import { useEffect, useMemo, useState } from 'react';
import { App, Button, Layout, Menu, Modal, Table, Tag, Typography, Spin } from 'antd';
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
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BulbOutlined,
  BulbFilled,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { checkAndDownloadSilently, installUpdate, listBackups } from '@/api/tauri';
import { formatFileSize } from '@/utils/format';
import { formatError } from '@/utils/formatError';
import { hasUnsavedChanges } from '@/utils/unsavedGuard';
import { APP_VERSION } from '@/constants/version';
import { useThemeMode } from '@/theme/ThemeContext';

const { Header, Sider, Content } = Layout;
const { Paragraph, Text } = Typography;

type NavItem = { key: string; icon: React.ReactNode; label: string };

/** 侧边栏导航项（扁平定义，用于选中态匹配与标题回显） */
const NAV_ITEMS: NavItem[] = [
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

/** 菜单分组定义：首页独立 + 业务组 + 数据组 + 系统设置独立 */
const MENU_GROUPS = [
  {
    key: 'grp-business',
    label: '业务',
    children: ['/prescription', '/patients', '/history'],
  },
  {
    key: 'grp-data',
    label: '数据',
    children: ['/medicines', '/inventory', '/statistics', '/batch-import'],
  },
] as const;

/** 快捷键帮助清单（F1 弹窗展示） */
const SHORTCUT_LIST = [
  { key: 'Ctrl + 1 ~ 9', desc: '快速切换页面（按菜单顺序）' },
  { key: 'Ctrl + S', desc: '保存处方（开处方页）' },
  { key: 'F1', desc: '打开/关闭本快捷键帮助' },
];

export default function MainLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { message, modal } = App.useApp();
  const { mode: themeMode, toggle: toggleTheme } = useThemeMode();
  const [installing, setInstalling] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  // 默认展开所有分组，便于用户发现功能
  const [openKeys, setOpenKeys] = useState<string[]>(['grp-business', 'grp-data']);

  // 全局快捷键：Ctrl+1~9 切换页面；F1 打开帮助
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F1') {
        e.preventDefault(); // 阻止浏览器/WebView 默认帮助行为
        setHelpOpen((v) => !v);
        return;
      }
      if ((e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey) {
        const n = Number(e.key);
        if (Number.isInteger(n) && n >= 1 && n <= NAV_ITEMS.length) {
          e.preventDefault();
          const target = NAV_ITEMS[n - 1].key;
          if (target === location.pathname) return;
          if (hasUnsavedChanges()) {
            // 开处方页有未保存内容：确认后跳转，避免误触快捷键丢失录入
            modal.confirm({
              title: '存在未保存的处方内容',
              content: '离开当前页面后未保存的处方明细将丢失，确定要离开吗？',
              okText: '离开',
              cancelText: '留在此页',
              okButtonProps: { danger: true },
              onOk: () => navigate(target),
            });
          } else {
            navigate(target);
          }
        }
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [navigate, location.pathname, modal]);

  // 备份提醒：距最近一次备份超过 7 天（或从未备份）时提示，商业数据安全标配
  useEffect(() => {
    const timer = setTimeout(() => {
      listBackups()
        .then((entries) => {
          const latest = entries
            .map((b) => b.created_at)
            .sort()
            .at(-1);
          const stale =
            !latest ||
            Date.now() - new Date(latest.replace(' ', 'T')).getTime() > 7 * 24 * 3600 * 1000;
          if (!stale) return;
          modal.confirm({
            title: latest ? '数据库备份已超过 7 天' : '尚未创建过数据库备份',
            width: 460,
            content: (
              <Typography.Paragraph type="secondary" style={{ marginBottom: 0 }}>
                备份可在意外断电、误删等情况下恢复全部经营数据。建议每周至少备份一次，
                备份文件保存在应用数据目录的 backups/ 子目录中。
              </Typography.Paragraph>
            ),
            okText: '前往备份',
            cancelText: '稍后',
            onOk: () => navigate('/settings'),
          });
        })
        .catch(() => {
          // 提醒失败不影响使用
        });
    }, 5000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 启动时静默检查更新：仅触发一次，失败不提示
  useEffect(() => {
    let cancelled = false;
    // 延迟 1.5s，避免与首屏数据请求争抢网络
    const timer = setTimeout(() => {
      checkAndDownloadSilently(APP_VERSION)
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
                      当前 v{APP_VERSION}
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
                  message.error(`启动安装失败：${formatError(e)}`);
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
        .catch((err) => {
          // 静默失败：不干扰用户启动，但输出 console.warn 便于开发者排查
          console.warn('[updater] 静默更新检查失败:', err);
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

  // 根据选中项自动展开所属分组
  useEffect(() => {
    const groupOfSelected = MENU_GROUPS.find((g) =>
      g.children.some((c) => c === selectedKey),
    );
    if (groupOfSelected && !openKeys.includes(groupOfSelected.key)) {
      setOpenKeys((prev) => [...prev, groupOfSelected.key]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedKey]);

  const buildMenuItems = useMemo((): MenuProps['items'] => {
    const findItem = (key: string) => NAV_ITEMS.find((i) => i.key === key)!;
    const linkLabel = (key: string) => {
      const item = findItem(key);
      return <Link to={item.key}>{item.label}</Link>;
    };

    const items: NonNullable<MenuProps['items']> = [
      {
        key: '/',
        icon: findItem('/').icon,
        label: linkLabel('/'),
      },
      ...MENU_GROUPS.map((g) => ({
        key: g.key,
        label: g.label,
        children: g.children.map((k) => ({
          key: k,
          icon: findItem(k).icon,
          label: linkLabel(k),
        })),
      })),
      {
        key: '/settings',
        icon: findItem('/settings').icon,
        label: linkLabel('/settings'),
      },
    ];
    return items;
    // NAV_ITEMS/MENU_GROUPS 为模块级常量，无需入依赖
  }, []);

  const currentLabel = NAV_ITEMS.find((item) => item.key === selectedKey)?.label ?? '首页概览';

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={208}
        collapsedWidth={64}
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        className="tcm-sider"
      >
        <div className={`tcm-logo${collapsed ? ' tcm-logo-collapsed' : ''}`}>
          <div className="tcm-logo-icon">本</div>
          {!collapsed && (
            <div className="tcm-logo-text">
              中药材
              <br />
              销售管理系统
            </div>
          )}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          openKeys={collapsed ? [] : openKeys}
          onOpenChange={(keys) => setOpenKeys(keys as string[])}
          items={buildMenuItems}
          style={{ borderRight: 0 }}
          inlineCollapsed={collapsed}
        />
      </Sider>
      <Layout>
        <Header className="tcm-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="tcm-collapse-btn"
            />
            <span className="tcm-header-title">{currentLabel}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span className="tcm-header-date">{formatToday()}</span>
            <Button
              type="text"
              icon={<QuestionCircleOutlined />}
              onClick={() => setHelpOpen(true)}
              title="键盘快捷键（F1）"
              className="tcm-collapse-btn"
            />
            <Button
              type="text"
              icon={themeMode === 'light' ? <BulbOutlined /> : <BulbFilled />}
              onClick={toggleTheme}
              title={themeMode === 'light' ? '切换到深色模式' : '切换到浅色模式'}
              className="tcm-collapse-btn"
            />
          </div>
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

      {/* 帮助与关于弹窗（F1 / 顶栏问号触发） */}
      <Modal
        title="帮助与关于"
        open={helpOpen}
        onCancel={() => setHelpOpen(false)}
        footer={null}
        width={480}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '12px 16px',
            marginBottom: 16,
            background: 'var(--primary-light)',
            borderRadius: 'var(--radius-md)',
          }}
        >
          <div className="tcm-logo-icon" style={{ width: 40, height: 40, fontSize: 22 }}>
            本
          </div>
          <div>
            <div style={{ fontWeight: 600, fontFamily: 'var(--font-display)' }}>
              中药材销售管理系统
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              版本 v{APP_VERSION} · 数据存储于本机，不经云端传输
            </div>
          </div>
        </div>
        <Table
          rowKey="key"
          size="small"
          pagination={false}
          dataSource={SHORTCUT_LIST}
          columns={[
            {
              title: '快捷键',
              dataIndex: 'key',
              key: 'key',
              width: 150,
              render: (v: string) => <Typography.Text keyboard>{v}</Typography.Text>,
            },
            { title: '功能', dataIndex: 'desc', key: 'desc' },
          ]}
        />
        <Typography.Paragraph type="secondary" style={{ marginTop: 12, marginBottom: 0, fontSize: 12 }}>
          提示：Ctrl+1 对应菜单第一项「首页概览」，依次类推至 Ctrl+9「系统设置」。
          数据备份与软件更新位于「系统设置」页。
        </Typography.Paragraph>
      </Modal>
    </Layout>
  );
}
