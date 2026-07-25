import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Alert,
  App,
  Button,
  Card,
  Descriptions,
  Popconfirm,
  Progress,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  CheckCircleOutlined,
  CloudDownloadOutlined,
  DatabaseOutlined,
  DownloadOutlined,
  FileSearchOutlined,
  ReloadOutlined,
  RollbackOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import {
  checkForUpdate,
  createBackup,
  downloadUpdate,
  installUpdate,
  listBackups,
  listOperationLogs,
  restoreBackup,
} from '@/api/tauri';
import EmptyState from '@/components/EmptyState';
import { compareVersions, formatFileSize } from '@/utils/format';
import { formatError } from '@/utils/formatError';
import type { BackupEntry, DownloadProgress, OperationLog, UpdateInfo } from '@/types';

const { Paragraph, Text } = Typography;

/** 当前应用版本（与 Cargo.toml / tauri.conf.json 对齐） */
const CURRENT_VERSION = '0.3.8';

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { message, modal } = App.useApp();

  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [downloadProgress, setDownloadProgress] = useState<DownloadProgress | null>(null);
  const [downloadedPath, setDownloadedPath] = useState<string>('');
  const [checking, setChecking] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [logType, setLogType] = useState<string | undefined>(undefined);

  const { data: backups, isLoading: backupsLoading } = useQuery({
    queryKey: ['backups'],
    queryFn: listBackups,
  });

  const { data: operationLogs, isLoading: logsLoading } = useQuery({
    queryKey: ['operation-logs', logType],
    queryFn: () => listOperationLogs(logType, undefined, undefined, undefined, 100),
  });

  const checkUpdateMutation = useMutation({
    mutationFn: checkForUpdate,
    onSuccess: (info) => {
      setUpdateInfo(info);
      if (!info.version) {
        message.warning('未获取到版本信息');
        return;
      }
      const hasNewVersion = compareVersions(info.version, CURRENT_VERSION) > 0;
      if (hasNewVersion) {
        modal.info({
          title: '发现新版本',
          width: 560,
          content: (
            <div>
              <Paragraph>
                <Text strong>版本：</Text>
                <Tag color="blue">v{info.version}</Tag>
                <Text type="secondary" style={{ marginLeft: 8 }}>
                  当前 v{CURRENT_VERSION}
                </Text>
              </Paragraph>
              {info.release_name && (
                <Paragraph style={{ marginTop: 4 }}>
                  <Text strong>标题：</Text>
                  {info.release_name}
                </Paragraph>
              )}
              {info.file_size > 0 && (
                <Paragraph>
                  <Text strong>安装包大小：</Text>
                  {formatFileSize(info.file_size)}
                </Paragraph>
              )}
              <Paragraph style={{ marginTop: 8 }}>
                <Text strong>更新日志：</Text>
              </Paragraph>
              <pre
                style={{
                  maxHeight: 240,
                  overflow: 'auto',
                  background: '#f5f7fa',
                  padding: 8,
                  borderRadius: 4,
                  fontSize: 12,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {info.changelog || '（无更新日志）'}
              </pre>
            </div>
          ),
          okText: '关闭',
        });
      } else {
        message.success(`当前已是最新版本（v${CURRENT_VERSION}）`);
      }
    },
    onError: (e: unknown) => message.error(`检查更新失败：${formatError(e)}`),
    onSettled: () => setChecking(false),
  });

  const downloadMutation = useMutation({
    mutationFn: (url: string) =>
      downloadUpdate(url, (p) => setDownloadProgress(p)),
    onSuccess: (path) => {
      setDownloadedPath(path);
      message.success(`下载完成：${path}`);
    },
    onError: (e: unknown) => message.error(`下载失败：${formatError(e)}`),
    onSettled: () => setDownloading(false),
  });

  const createBackupMutation = useMutation({
    mutationFn: createBackup,
    onSuccess: (info) => {
      message.success(`备份成功：${info.backup_path}`);
      queryClient.invalidateQueries({ queryKey: ['backups'] });
    },
    onError: (e: unknown) => message.error(`备份失败：${formatError(e)}`),
  });

  const restoreMutation = useMutation({
    mutationFn: restoreBackup,
    onSuccess: () => {
      message.success('还原成功，正在刷新应用...');
      // 强制整体刷新，比 invalidateQueries 更安全：
      // 避免组件持有旧引用导致新旧数据混合状态
      setTimeout(() => window.location.reload(), 800);
    },
    onError: (e: unknown) => message.error(`还原失败：${formatError(e)}`),
  });

  const installMutation = useMutation({
    // 手动安装路径：显式 silent=false，走 NSIS 安装向导 UI（非静默）
    mutationFn: (path: string) => installUpdate(path, false),
    onSuccess: () => {
      message.success('安装程序已启动，请按安装向导完成升级');
    },
    onError: (e: unknown) => message.error(`启动安装程序失败：${formatError(e)}`),
  });

  const handleCheckUpdate = () => {
    setChecking(true);
    setDownloadedPath('');
    setDownloadProgress(null);
    checkUpdateMutation.mutate();
  };

  const handleDownloadUpdate = () => {
    if (!updateInfo?.download_url) {
      message.warning('未找到可下载的 .exe 安装包');
      return;
    }
    setDownloading(true);
    setDownloadProgress({ downloaded: 0, total: updateInfo.file_size || 0 });
    setDownloadedPath('');
    downloadMutation.mutate(updateInfo.download_url);
  };

  const handleInstallUpdate = () => {
    if (!downloadedPath) {
      message.warning('请先下载更新');
      return;
    }
    modal.confirm({
      title: '确认安装更新',
      content: '将启动下载好的安装程序，请保存当前正在编辑的内容后继续。',
      okText: '启动安装',
      cancelText: '取消',
      onOk: () => installMutation.mutateAsync(downloadedPath),
    });
  };

  const backupColumns: ColumnsType<BackupEntry> = [
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 110,
      render: (v: number) => formatFileSize(v),
    },
    {
      title: 'MD5',
      dataIndex: 'md5',
      key: 'md5',
      ellipsis: true,
      render: (v: string) => <Text code style={{ fontSize: 12 }}>{v}</Text>,
    },
    {
      title: '路径',
      dataIndex: 'backup_path',
      key: 'backup_path',
      ellipsis: true,
      render: (v: string) => <Text type="secondary" style={{ fontSize: 12 }}>{v}</Text>,
    },
    {
      title: '操作',
      key: 'action',
      width: 110,
      fixed: 'right',
      render: (_v, r) => (
        <Popconfirm
          title="确认还原此备份？"
          description="当前数据库将被覆盖，建议先创建新备份"
          onConfirm={() => restoreMutation.mutate(r.backup_path)}
          okText="还原"
          cancelText="取消"
        >
          <Button type="link" size="small" icon={<RollbackOutlined />} loading={restoreMutation.isPending}>
            还原
          </Button>
        </Popconfirm>
      ),
    },
  ];

  const progressPercent =
    downloadProgress && downloadProgress.total > 0
      ? Math.min(100, Math.round((downloadProgress.downloaded / downloadProgress.total) * 100))
      : 0;

  const hasNewVersion =
    updateInfo &&
    updateInfo.version &&
    compareVersions(updateInfo.version, CURRENT_VERSION) > 0;

  // 操作日志表格列
  const logColumns: ColumnsType<OperationLog> = [
    {
      title: '类型',
      dataIndex: 'operation_type',
      key: 'operation_type',
      width: 90,
      render: (t: string) => {
        const colorMap: Record<string, string> = {
          CREATE: 'green',
          UPDATE: 'blue',
          DELETE: 'red',
          STOCK: 'orange',
          IMPORT: 'purple',
        };
        return <Tag color={colorMap[t] ?? 'default'}>{t}</Tag>;
      },
    },
    {
      title: '目标',
      dataIndex: 'target_type',
      key: 'target_type',
      width: 100,
    },
    {
      title: '目标ID',
      dataIndex: 'target_id',
      key: 'target_id',
      width: 80,
      render: (v: number) => (v > 0 ? v : '-'),
    },
    {
      title: '详情',
      dataIndex: 'details',
      key: 'details',
      ellipsis: true,
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
    },
  ];

  const LOG_TYPE_OPTIONS = [
    { label: '全部', value: '' },
    { label: '创建', value: 'CREATE' },
    { label: '更新', value: 'UPDATE' },
    { label: '删除', value: 'DELETE' },
    { label: '库存', value: 'STOCK' },
    { label: '导入', value: 'IMPORT' },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">系统设置</h1>
        <p className="page-subtitle">管理数据备份、还原与软件更新</p>
      </div>

      {/* 当前版本信息 */}
      <Card style={{ marginBottom: 16 }}>
        <Descriptions title="版本信息" column={2} size="small">
          <Descriptions.Item label="当前版本">
            <Tag color="blue">v{CURRENT_VERSION}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="最新版本">
            {updateInfo ? (
              <Tag color={hasNewVersion ? 'red' : 'green'}>
                v{updateInfo.version || '未知'}
              </Tag>
            ) : (
              <Text type="secondary">未检查</Text>
            )}
          </Descriptions.Item>
          {updateInfo?.file_size ? (
            <Descriptions.Item label="安装包大小">
              {formatFileSize(updateInfo.file_size)}
            </Descriptions.Item>
          ) : null}
          {updateInfo?.release_name ? (
            <Descriptions.Item label="发布标题">
              {updateInfo.release_name}
            </Descriptions.Item>
          ) : null}
        </Descriptions>

        <Space style={{ marginTop: 16 }} wrap>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleCheckUpdate}
            loading={checking}
          >
            检查更新
          </Button>
          <Button
            type="primary"
            icon={<CloudDownloadOutlined />}
            onClick={handleDownloadUpdate}
            disabled={!hasNewVersion || !updateInfo?.download_url || downloading}
            loading={downloading}
          >
            下载更新
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={handleInstallUpdate}
            disabled={!downloadedPath || installMutation.isPending}
            loading={installMutation.isPending}
          >
            启动安装程序
          </Button>
        </Space>

        {downloading && downloadProgress && (
          <div style={{ marginTop: 16 }}>
            <Progress
              percent={progressPercent}
              status={progressPercent >= 100 ? 'success' : 'active'}
              format={(p) =>
                `${p}% · ${formatFileSize(downloadProgress.downloaded)} / ${formatFileSize(
                  downloadProgress.total,
                )}`
              }
            />
          </div>
        )}
        {downloadedPath && !downloading && (
          <Alert
            type="success"
            showIcon
            icon={<CheckCircleOutlined />}
            style={{ marginTop: 16 }}
            message={
              <span>
                下载完成：<Text code>{downloadedPath}</Text>
              </span>
            }
          />
        )}
        {updateInfo?.changelog && hasNewVersion && (
          <Alert
            type="info"
            style={{ marginTop: 16 }}
            message={<Text strong>更新日志（v{updateInfo.version}）</Text>}
            description={
              <pre
                style={{
                  maxHeight: 200,
                  overflow: 'auto',
                  margin: 0,
                  fontSize: 12,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {updateInfo.changelog}
              </pre>
            }
          />
        )}
      </Card>

      {/* 数据备份与恢复 */}
      <Card
        title={
          <Space>
            <DatabaseOutlined />
            <span>数据备份与恢复</span>
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={() => createBackupMutation.mutate()}
            loading={createBackupMutation.isPending}
          >
            立即创建备份
          </Button>
        }
      >
        <Table<BackupEntry>
          rowKey="backup_path"
          size="small"
          loading={backupsLoading}
          columns={backupColumns}
          dataSource={backups}
          scroll={{ x: 900 }}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          locale={{ emptyText: <EmptyState title="暂无备份" description="点击上方按钮创建第一个备份" /> }}
        />
        <Paragraph type="secondary" style={{ marginTop: 12, marginBottom: 0, fontSize: 13 }}>
          备份文件保存在应用数据目录下的 <Text code>backups/</Text> 子目录中。
          还原将用备份覆盖当前数据库，建议操作前先创建新备份。
        </Paragraph>
      </Card>

      {/* 操作日志 */}
      <Card
        title={
          <Space>
            <FileSearchOutlined />
            <span>操作日志（最近 100 条）</span>
          </Space>
        }
        extra={
          <Select
            placeholder="筛选操作类型"
            allowClear
            style={{ width: 140 }}
            options={LOG_TYPE_OPTIONS}
            value={logType}
            onChange={(v) => setLogType(v || undefined)}
          />
        }
        style={{ marginTop: 16 }}
      >
        <Table<OperationLog>
          rowKey="id"
          size="small"
          loading={logsLoading}
          columns={logColumns}
          dataSource={operationLogs}
          scroll={{ x: 700 }}
          pagination={{ pageSize: 10, showSizeChanger: true }}
          locale={{
            emptyText: <EmptyState title="暂无操作日志" description="系统操作后将自动记录日志" />,
          }}
        />
      </Card>
    </div>
  );
}

