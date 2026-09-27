import { useRef, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import {
  Alert,
  App,
  Button,
  Progress,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  DownloadOutlined,
  ExportOutlined,
  InboxOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import {
  batchImportMedicines,
  downloadImportTemplate,
  exportMedicinesCsv,
  saveTextToDownloads,
} from '@/api/tauri';
import EmptyState from '@/components/EmptyState';
import { parseCsvText } from '@/utils/csv';
import { formatError } from '@/utils/formatError';
import type { BatchImportResult, MedicineImportRecord } from '@/types';

const { Paragraph, Text } = Typography;

export default function BatchImportPage() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [records, setRecords] = useState<MedicineImportRecord[]>([]);
  const [fileName, setFileName] = useState<string>('');
  const [progress, setProgress] = useState<number>(0);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<BatchImportResult | null>(null);

  const importMutation = useMutation({
    mutationFn: batchImportMedicines,
    onSuccess: (data) => {
      message.success(`导入完成：新增 ${data.inserted} 条，更新 ${data.updated} 条`);
      queryClient.invalidateQueries({ queryKey: ['medicines'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      // 导入会新建批次，影响效期预警横幅
      queryClient.invalidateQueries({ queryKey: ['expiring-batches'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setResult(data);
    },
    onError: (e: unknown) => message.error(formatError(e)),
    onSettled: () => {
      setImporting(false);
      setProgress(100);
    },
  });

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setResult(null);
    setProgress(0);
    try {
      const text = await file.text();
      const parsed = parseCsvText(text);
      if (parsed.length === 0) {
        message.warning('文件中未解析到有效数据');
        setRecords([]);
        return;
      }
      setRecords(parsed);
      message.success(`已加载 ${parsed.length} 条记录`);
    } catch (err) {
      message.error(`解析文件失败：${err instanceof Error ? err.message : String(err)}`);
      setRecords([]);
    } finally {
      // 重置 input，便于重新选择同一文件
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handlePickFile = () => fileInputRef.current?.click();

  const handleImport = () => {
    if (records.length === 0) {
      message.warning('请先选择要导入的文件');
      return;
    }
    setImporting(true);
    setProgress(10);
    setResult(null);
    // 模拟进度推进（后端单次同步返回，进度靠估算）
    const timer = setInterval(() => {
      setProgress((p) => (p < 90 ? p + 5 : p));
    }, 200);
    importMutation.mutate(records, {
      onSettled: () => clearInterval(timer),
    });
  };

  const handleDownloadTemplate = async () => {
    try {
      const csv = await downloadImportTemplate();
      const path = await saveTextToDownloads('药材导入模板.csv', csv);
      message.success(`模板已保存到：${path}`);
    } catch (e) {
      message.error(formatError(e));
    }
  };

  const handleExportCsv = async () => {
    try {
      const csv = await exportMedicinesCsv();
      // 本地日期（dayjs），避免 UTC 口径在 0-8 点把文件名日期标成前一天
      const ts = dayjs().format('YYYYMMDD');
      const path = await saveTextToDownloads(`medicines_export_${ts}.csv`, csv);
      message.success(`已导出到：${path}`);
    } catch (e) {
      message.error(formatError(e));
    }
  };

  // 预览前 5 行
  const preview: MedicineImportRecord[] = records.slice(0, 5);

  const previewColumns: ColumnsType<MedicineImportRecord> = [
    { title: '名称', dataIndex: 'name', key: 'name', width: 120 },
    { title: '别名', dataIndex: 'alias', key: 'alias', width: 120, ellipsis: true },
    { title: '分类', dataIndex: 'category', key: 'category', width: 100 },
    { title: '性味', key: 'nature_taste', width: 120, render: (_v, r) => `${r.nature ?? ''} ${r.taste ?? ''}`.trim() || '-' },
    { title: '归经', dataIndex: 'meridian', key: 'meridian', width: 120, ellipsis: true },
    { title: '功效', dataIndex: 'efficacy', key: 'efficacy', ellipsis: true },
    { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 80 },
    { title: '单位', dataIndex: 'unit', key: 'unit', width: 70 },
    { title: '单价', dataIndex: 'price', key: 'price', width: 90 },
    { title: '最低库存', dataIndex: 'min_stock', key: 'min_stock', width: 100 },
  ];

  const errorList = result?.errors.slice(0, 10) ?? [];
  const hasMoreErrors = (result?.errors.length ?? 0) > 10;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">批量导入药材</h1>
        <p className="page-subtitle">选择 CSV 文件批量导入或更新药材（按名称 UPSERT），支持下载导入模板与导出现有数据</p>
      </div>

      <div className="table-card" style={{ marginBottom: 16 }}>
        <Space wrap>
          <Button
            type="primary"
            icon={<InboxOutlined />}
            onClick={handlePickFile}
            disabled={importing}
          >
            选择 CSV 文件
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleDownloadTemplate} disabled={importing}>
            下载导入模板
          </Button>
          <Button icon={<ExportOutlined />} onClick={handleExportCsv} disabled={importing}>
            导出全量药材
          </Button>
          {fileName && (
            <Text type="secondary">
              已选择：<Text strong>{fileName}</Text> （共 {records.length} 条）
            </Text>
          )}
        </Space>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,text/csv"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </div>

      {/* 预览 */}
      <div className="table-card" style={{ marginBottom: 16 }}>
        <div className="table-title">数据预览（前 5 行）</div>
        {preview.length > 0 ? (
          <Table<MedicineImportRecord>
            rowKey={(_, i) => `preview-${i}`}
            size="small"
            columns={previewColumns}
            dataSource={preview}
            pagination={false}
            scroll={{ x: 1100 }}
          />
        ) : (
          <EmptyState title="请选择文件查看预览" />
        )}
      </div>

      {/* 导入操作 */}
      <div className="table-card" style={{ marginBottom: 16 }}>
        <div className="table-title">导入操作</div>
        {(importing || progress > 0) && (
          <Progress
            percent={progress}
            status={importing ? 'active' : result && result.errors.length > 0 ? 'exception' : 'success'}
            style={{ marginBottom: 16 }}
          />
        )}
        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleImport}
            loading={importing}
            disabled={records.length === 0}
          >
            开始导入（{records.length} 条）
          </Button>
        </Space>
      </div>

      {/* 结果与错误日志 */}
      {result ? (
        <div className="table-card">
          <div className="table-title">导入结果</div>
          <Space size="large" style={{ marginBottom: 16 }}>
            <Tag color="green">新增 {result.inserted} 条</Tag>
            <Tag color="blue">更新 {result.updated} 条</Tag>
            <Tag color={result.errors.length > 0 ? 'red' : 'default'}>
              错误 {result.errors.length} 条
            </Tag>
          </Space>
          {errorList.length > 0 && (
            <>
              <Alert
                type={hasMoreErrors ? 'warning' : 'error'}
                showIcon
                style={{ marginBottom: 8 }}
                message={
                  hasMoreErrors
                    ? `仅显示前 10 条错误（共 ${result.errors.length} 条）`
                    : `共 ${result.errors.length} 条错误`
                }
              />
              <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--danger-color)' }}>
                {errorList.map((err, i) => (
                  <li key={i} style={{ fontSize: 13, lineHeight: 1.8 }}>
                    {err}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      ) : (
        <div className="table-card">
          <div className="table-title">导入日志</div>
          <EmptyState title="暂无导入日志" />
        </div>
      )}

      {/* 帮助说明 */}
      <div className="table-card" style={{ marginTop: 16 }}>
        <div className="table-title">导入说明</div>
        <Paragraph type="secondary" style={{ fontSize: 13, lineHeight: 1.8, marginBottom: 0 }}>
          <p style={{ margin: '4px 0' }}>支持的文件格式：<Text strong>CSV（UTF-8 编码，含 BOM 与不含 BOM 均可）</Text></p>
          <p style={{ margin: '4px 0' }}>必填字段：<Text code>name</Text>（药材名称）</p>
          <p style={{ margin: '4px 0' }}>
            可选字段：alias、category、nature、taste、meridian、efficacy、indications、usage、dosage、
            contraindication、notes、quantity、unit、price、min_stock
          </p>
          <p style={{ margin: '4px 0' }}>说明：重复的药材名称将更新其信息与库存，不会重复创建；数值字段支持字符串形式提交，后端做类型转换保护。</p>
          <p style={{ margin: '4px 0' }}>导出：导出的 CSV 不含库存信息，仅药材基础字段，便于在 Excel 中编辑后回导。</p>
        </Paragraph>
      </div>
    </div>
  );
}
