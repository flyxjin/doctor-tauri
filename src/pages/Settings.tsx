import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import {
  Alert,
  App,
  Button,
  Card,
  DatePicker,
  Descriptions,
  Popconfirm,
  Progress,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';

const { RangePicker } = DatePicker;
import type { ColumnsType } from 'antd/es/table';
import {
  CheckCircleOutlined,
  CloudDownloadOutlined,
  DatabaseOutlined,
  DeleteOutlined,
  DownloadOutlined,
  ExportOutlined,
  FileSearchOutlined,
  ImportOutlined,
  ReloadOutlined,
  RollbackOutlined,
  SaveOutlined,
  SwapOutlined,
} from '@ant-design/icons';
import {
  checkForUpdate,
  createBackup,
  deleteBackup,
  downloadImportTemplate,
  downloadUpdate,
  exportMedicinesCsv,
  installUpdate,
  listBackups,
  listOperationLogs,
  restoreBackup,
  saveTextToDownloads,
} from '@/api/tauri';
import EmptyState from '@/components/EmptyState';
import QueryErrorAlert from '@/components/QueryErrorAlert';
import { compareVersions, formatFileSize } from '@/utils/format';
import { formatError } from '@/utils/formatError';
import { APP_VERSION } from '@/constants/version';
import type { BackupEntry, DownloadProgress, OperationLog, UpdateInfo } from '@/types';

const { Paragraph, Text } = Typography;

// 下载状态的模块级存储：下载期间切换页面会卸载本组件，
// 组件 state 丢失会导致"下载完成后回到设置页拿不到安装包路径"。
// 把关键结果提升到模块级，重新挂载时恢复展示。
let completedDownloadPath = '';
let activeDownload: { url: string } | null = null;

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { message, modal } = App.useApp();

  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [downloadProgress, setDownloadProgress] = useState<DownloadProgress | null>(null);
  const [downloadedPath, setDownloadedPath] = useState<string>(() => completedDownloadPath);
  // 进入页面时若已有后台下载在进行，展示只读提示（进度回调属于原组件实例，无法续接）
  const [bgDownloading, setBgDownloading] = useState(() => activeDownload !== null);
  const [checking, setChecking] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [logType, setLogType] = useState<string | undefined>(undefined);
  // 操作日志日期范围筛选（后端支持半开区间过滤，保留 created_at 索引）
  const [logDateRange, setLogDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
  // 数据导入导出入口的加载态
  const [templateLoading, setTemplateLoading] = useState(false);
  const [exportMedLoading, setExportMedLoading] = useState(false);

  const { data: backups, isLoading: backupsLoading, isError: backupsError, error: backupsErr, refetch: refetchBackups, isFetching: backupsFetching } = useQuery({
    queryKey: ['backups'],
    queryFn: listBackups,
  });

  const { data: operationLogs, isLoading: logsLoading, isError: logsError, error: logsErr, refetch: refetchLogs, isFetching: logsFetching } = useQuery({
    queryKey: ['operation-logs', logType, logDateRange?.[0]?.format('YYYY-MM-DD'), logDateRange?.[1]?.format('YYYY-MM-DD')],
    queryFn: () =>
      listOperationLogs(
        logType,
        undefined,
        logDateRange?.[0]?.format('YYYY-MM-DD'),
        logDateRange?.[1]?.format('YYYY-MM-DD'),
        100,
      ),
  });

  const checkUpdateMutation = useMutation({
    mutationFn: checkForUpdate,
    onSuccess: (info) => {
      setUpdateInfo(info);
      if (!info.version) {
        message.warning('未获取到版本信息');
        return;
      }
      const hasNewVersion = compareVersions(info.version, APP_VERSION) > 0;
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
                  当前 v{APP_VERSION}
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
                  background: 'var(--bg-color)', color: 'var(--text-color)',
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
        message.success(`当前已是最新版本（v${APP_VERSION}）`);
      }
    },
    onError: (e: unknown) => message.error(`检查更新失败：${formatError(e)}`),
    onSettled: () => setChecking(false),
  });

  const downloadMutation = useMutation({
    mutationFn: async (url: string) => {
      activeDownload = { url };
      try {
        const path = await downloadUpdate(
          url,
          updateInfo?.file_size ?? 0,
          updateInfo?.checksum ?? '',
          (p) => setDownloadProgress(p),
        );
        completedDownloadPath = path;
        return path;
      } finally {
        activeDownload = null;
      }
    },
    onSuccess: (path) => {
      setDownloadedPath(path);
      message.success(`下载完成：${path}`);
    },
    onError: (e: unknown) => message.error(`下载失败：${formatError(e)}`),
    onSettled: () => setDownloading(false),
  });

  // 后台下载进行中：轮询模块级完成标记，下载完成后在本页恢复展示安装入口
  useEffect(() => {
    if (!bgDownloading) return;
    const timer = setInterval(() => {
      if (!activeDownload && completedDownloadPath) {
        setDownloadedPath(completedDownloadPath);
        setBgDownloading(false);
        setDownloadProgress(null);
        message.success(`后台下载已完成：${completedDownloadPath}`);
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [bgDownloading, message]);

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

  const deleteBackupMutation = useMutation({
    mutationFn: deleteBackup,
    onSuccess: () => {
      message.success('备份已删除');
      queryClient.invalidateQueries({ queryKey: ['backups'] });
    },
    onError: (e: unknown) => message.error(`删除备份失败：${formatError(e)}`),
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

  /** 下载药材导入模板（含样本数据）到系统下载目录 */
  const handleDownloadTemplate = async () => {
    setTemplateLoading(true);
    try {
      const csv = await downloadImportTemplate();
      const ts = dayjs().format('YYYYMMDD_HHmmss');
      const path = await saveTextToDownloads(`药材导入模板_${ts}.csv`, csv);
      message.success(`导入模板已下载到：${path}`);
    } catch (e) {
      message.error(`下载模板失败：${formatError(e)}`);
    } finally {
      setTemplateLoading(false);
    }
  };

  /** 导出全量药材库为 CSV（后端生成，含完整字段） */
  const handleExportAllMedicines = async () => {
    setExportMedLoading(true);
    try {
      const csv = await exportMedicinesCsv();
      const ts = dayjs().format('YYYYMMDD_HHmmss');
      const path = await saveTextToDownloads(`药材全量导出_${ts}.csv`, csv);
      message.success(`全量药材已导出到：${path}`);
    } catch (e) {
      message.error(`导出失败：${formatError(e)}`);
    } finally {
      setExportMedLoading(false);
    }
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
      title: '校验值',
      dataIndex: 'checksum',
      key: 'checksum',
      ellipsis: true,
      render: (v: string) => <Text code style={{ fontSize: 12 }}>{v || '-'}</Text>,
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
      width: 170,
      fixed: 'right',
      render: (_v, r) => (
        <Space size="small">
          <Popconfirm
            title="确认还原此备份？"
            description="当前数据库将被覆盖，建议先创建新备份"
            onConfirm={() => restoreMutation.mutate(r.backup_path)}
            okText="还原"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button type="link" size="small" icon={<RollbackOutlined />} loading={restoreMutation.isPending}>
              还原
            </Button>
          </Popconfirm>
          <Popconfirm
            title="确认删除此备份？"
            description="删除后无法恢复，建议保留近期至少一份备份"
            onConfirm={() => deleteBackupMutation.mutate(r.backup_path)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              loading={deleteBackupMutation.isPending}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
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
    compareVersions(updateInfo.version, APP_VERSION) > 0;

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
            <Tag color="blue">v{APP_VERSION}</Tag>
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
        {bgDownloading && !downloading && (
          <Alert
            type="info"
            showIcon
            style={{ marginTop: 16 }}
            message="更新包正在后台下载"
            description="下载期间可以离开本页面，完成后回到这里会自动显示安装入口。"
          />
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

      {/* 数据导入导出统一入口（ROADMAP 数据迁移向导精简版） */}
      <Card
        title={
          <Space>
            <SwapOutlined />
            <span>数据导入导出</span>
          </Space>
        }
        style={{ marginBottom: 16 }}
      >
        <Space wrap>
          <Button
            type="primary"
            icon={<ImportOutlined />}
            onClick={() => navigate('/batch-import')}
          >
            前往批量导入
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={handleDownloadTemplate}
            loading={templateLoading}
          >
            下载导入模板
          </Button>
          <Button
            icon={<ExportOutlined />}
            onClick={handleExportAllMedicines}
            loading={exportMedLoading}
          >
            导出全量药材 CSV
          </Button>
        </Space>
        <Paragraph type="secondary" style={{ marginTop: 12, marginBottom: 0, fontSize: 13 }}>
          批量导入支持 CSV 格式，导入前请先下载模板核对字段；药材导出含全部字段，
          可用于数据备份或在 Excel 中批量维护后重新导入。
        </Paragraph>
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
        {backupsError && (
          <QueryErrorAlert
            error={backupsErr}
            onRetry={() => refetchBackups()}
            retrying={backupsFetching}
            message="加载备份列表失败"
          />
        )}
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
          <Space>
            <RangePicker
              size="small"
              value={logDateRange}
              onChange={(dates) =>
                setLogDateRange(dates?.[0] && dates?.[1] ? [dates[0], dates[1]] : null)
              }
              placeholder={['开始日期', '结束日期']}
              allowClear
            />
            <Select
              placeholder="筛选操作类型"
              allowClear
              style={{ width: 140 }}
              options={LOG_TYPE_OPTIONS}
              value={logType}
              onChange={(v) => setLogType(v || undefined)}
            />
          </Space>
        }
        style={{ marginTop: 16 }}
      >
        {logsError && (
          <QueryErrorAlert
            error={logsErr}
            onRetry={() => refetchLogs()}
            retrying={logsFetching}
            message="加载操作日志失败"
          />
        )}
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

