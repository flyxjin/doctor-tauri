import { useEffect, useMemo, useState } from 'react';
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Alert,
  App,
  Button,
  DatePicker,
  Descriptions,
  Drawer,
  Input,
  Popconfirm,
  Space,
  Statistic,
  Table,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { CopyOutlined, DeleteOutlined, EyeOutlined, ExportOutlined, FilePdfOutlined, PrinterOutlined } from '@ant-design/icons';
import dayjs, { type Dayjs } from 'dayjs';
import { deletePrescription, generatePrescriptionHtml, listPrescriptions } from '@/api/tauri';
import { exportHtmlAsPdf, printHtmlInIframe } from '@/utils/print';
import { useCopyToPrescription } from '@/hooks/useCopyToPrescription';
import { useCsvExport } from '@/hooks/useCsvExport';
import type { PrescriptionItem, PrescriptionWithItems } from '@/types';
import EmptyState from '@/components/EmptyState';
import QueryErrorAlert from '@/components/QueryErrorAlert';
import { formatError } from '@/utils/formatError';

const { RangePicker } = DatePicker;
const { Title } = Typography;

/** 日期快捷预设 */
type QuickKey = 'today' | 'week' | 'month' | 'quarter';
const QUICK_PRESETS: { key: QuickKey; label: string }[] = [
  { key: 'today', label: '今天' },
  { key: 'week', label: '近 7 天' },
  { key: 'month', label: '本月' },
  { key: 'quarter', label: '近 3 月' },
];

/** 根据预设 key 计算日期范围 */
function getPresetRange(key: QuickKey): [Dayjs, Dayjs] {
  const today = dayjs();
  switch (key) {
    case 'today':
      return [today.startOf('day'), today];
    case 'week':
      return [today.subtract(6, 'day').startOf('day'), today];
    case 'month':
      return [today.startOf('month'), today];
    case 'quarter':
      return [today.subtract(2, 'month').startOf('month'), today];
  }
}

export default function HistoryPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  const { message } = App.useApp();
  const [keyword, setKeyword] = useState('');
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  // 当前选中的日期预设；null 表示未选或用户自定义了日期范围
  const [quickKey, setQuickKey] = useState<QuickKey | null>(null);
  const [detail, setDetail] = useState<PrescriptionWithItems | null>(null);
  const [printingId, setPrintingId] = useState<number | null>(null);
  const [exportingPdfId, setExportingPdfId] = useState<number | null>(null);

  // CSV 导出：复用统一 hook（统一保存机制、时间戳格式、提示文案）
  const { exportCsv } = useCsvExport({ filenamePrefix: '处方历史', label: '处方记录' });

  // 后端日期筛选：将日期范围传入 SQL 查询，避免拉取全量再前端过滤
  const startDate = dateRange?.[0]?.format('YYYY-MM-DD');
  const endDate = dateRange?.[1]?.format('YYYY-MM-DD');

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['prescriptions', keyword, startDate, endDate],
    queryFn: () => listPrescriptions(keyword || undefined, startDate, endDate, 500),
    // 处方历史变更频率中等，缓存 1 分钟；新建/删除后由 mutation 失效
    staleTime: 60 * 1000,
    // 关键字/日期筛选切换时保留上一次结果，避免表格闪烁；仅搜索列表场景使用
    placeholderData: keepPreviousData,
  });

  // 从 Dashboard 跳转而来时，自动定位并打开对应处方详情
  const focusId = (location.state as { focusId?: number } | null)?.focusId;
  useEffect(() => {
    if (!focusId || !data || detail) return;
    const target = data.find((p) => p.id === focusId);
    if (target) {
      setDetail(target);
      // 消费后清除 location.state，避免返回时重复触发
      navigate(location.pathname, { replace: true, state: null });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusId, data]);

  // 汇总统计
  const summary = useMemo(() => {
    const list = data ?? [];
    const totalAmount = list.reduce((s, p) => s + p.total_amount, 0);
    const totalItems = list.reduce((s, p) => s + p.items.length, 0);
    return { count: list.length, totalAmount, totalItems };
  }, [data]);

  const deleteMutation = useMutation({
    mutationFn: deletePrescription,
    onSuccess: () => {
      message.success('处方已删除（库存已回扣）');
      queryClient.invalidateQueries({ queryKey: ['prescriptions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      // 删除处方会回扣库存并影响统计与患者视图；注意 ['prescriptions'] 前缀
      // 匹配不到 ['patient-prescriptions', ...] / ['patient-statistics', ...]
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      queryClient.invalidateQueries({ queryKey: ['expiring-batches'] });
      queryClient.invalidateQueries({ queryKey: ['patient-prescriptions'] });
      queryClient.invalidateQueries({ queryKey: ['patient-statistics'] });
      setDetail(null);
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  // 导出当前筛选结果为 CSV（统一走 saveTextToDownloads，与其它页面行为一致）
  const handleExportCsv = () => {
    const list = data ?? [];
    const rows: (string | number | null | undefined)[][] = [
      ['处方号', '患者姓名', '性别', '年龄', '诊断', '味数', '金额', '开方人', '开方时间'],
    ];
    for (const p of list) {
      rows.push([
        p.id ?? '',
        p.patient_name,
        p.patient_gender,
        p.patient_age ?? '',
        p.diagnosis,
        p.items.length,
        p.total_amount.toFixed(2),
        p.created_by,
        p.created_at ?? '',
      ]);
    }
    void exportCsv(rows, list.length);
  };

  const handlePrint = async (id: number) => {
    setPrintingId(id);
    try {
      const html = await generatePrescriptionHtml(id);
      await printHtmlInIframe(html);
      message.success('已发送至打印预览');
    } catch (e) {
      message.error(formatError(e));
    } finally {
      setPrintingId(null);
    }
  };

  /**
   * 导出处方为 PDF 文件
   *
   * 调用后端 generate_prescription_html 生成处方 HTML，
   * 再通过 iframe + window.print() 触发系统打印对话框。
   * 用户在对话框中选择「Microsoft Print to PDF」作为打印机即可保存为 PDF。
   */
  const handleExportPdf = async (id: number) => {
    setExportingPdfId(id);
    try {
      const html = await generatePrescriptionHtml(id);
      message.info('请在打印对话框中选择「Microsoft Print to PDF」作为打印机，然后点击保存');
      await exportHtmlAsPdf(html);
      message.success('已打开打印对话框，选择 PDF 打印机即可导出');
    } catch (e) {
      message.error(formatError(e));
    } finally {
      setExportingPdfId(null);
    }
  };

  /** 复制到处方：复用通用 hook，关闭详情 Drawer 后跳转 */
  const { copyToPrescription } = useCopyToPrescription(() => setDetail(null));
  const handleCopyToPrescription = (record: PrescriptionWithItems) => {
    copyToPrescription(record);
  };

  const columns: ColumnsType<PrescriptionWithItems> = [
    {
      title: '处方号',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      fixed: 'left',
    },
    { title: '患者', dataIndex: 'patient_name', key: 'patient_name', width: 100 },
    {
      title: '性别',
      dataIndex: 'patient_gender',
      key: 'patient_gender',
      width: 70,
    },
    { title: '年龄', dataIndex: 'patient_age', key: 'patient_age', width: 70 },
    {
      title: '诊断',
      dataIndex: 'diagnosis',
      key: 'diagnosis',
      ellipsis: true,
    },
    {
      title: '味数',
      key: 'item_count',
      width: 80,
      align: 'center',
      render: (_v, r) => r.items.length,
    },
    {
      title: '金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      width: 110,
      align: 'right',
      render: (v: number) => (
        <Tag color="blue" style={{ borderRadius: 4 }}>
          ¥{v.toFixed(2)}
        </Tag>
      ),
    },
    { title: '开方人', dataIndex: 'created_by', key: 'created_by', width: 100 },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_v, record) => (
        <Space size={2}>
          <Tooltip title="详情">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => setDetail(record)}
            />
          </Tooltip>
          <Tooltip title="复制到处方">
            <Button
              type="text"
              size="small"
              icon={<CopyOutlined />}
              onClick={() => handleCopyToPrescription(record)}
            />
          </Tooltip>
          <Tooltip title="打印">
            <Button
              type="text"
              size="small"
              icon={<PrinterOutlined />}
              loading={printingId === record.id}
              onClick={() => handlePrint(record.id!)}
            />
          </Tooltip>
          <Tooltip title="导出 PDF">
            <Button
              type="text"
              size="small"
              icon={<FilePdfOutlined />}
              loading={exportingPdfId === record.id}
              onClick={() => handleExportPdf(record.id!)}
            />
          </Tooltip>
          <Popconfirm
            title="确认删除该处方？"
            description="将回扣库存，此操作不可撤销"
            onConfirm={() => deleteMutation.mutate(record.id!)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="删除">
              <Button type="text" size="small" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const itemColumns: ColumnsType<PrescriptionItem> = [
    { title: '药材', dataIndex: 'medicine_name', key: 'medicine_name' },
    { title: '数量', dataIndex: 'quantity', key: 'quantity', width: 100 },
    { title: '单位', dataIndex: 'unit', key: 'unit', width: 80 },
    {
      title: '单价',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      align: 'right',
      render: (p: number) => `¥${p.toFixed(2)}`,
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 110,
      align: 'right',
      render: (a: number) => `¥${a.toFixed(2)}`,
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">处方历史</h1>
        <p className="page-subtitle">查询历史处方、查看明细、导出报表</p>
      </div>

      {/* 汇总统计（卡片化，与页面整体风格一致） */}
      <div className="quick-actions" style={{ display: 'flex', gap: 48 }}>
        <Statistic title="处方数" value={summary.count} loading={isLoading} />
        <Statistic title="总味数" value={summary.totalItems} loading={isLoading} />
        <Statistic
          title="总金额"
          value={summary.totalAmount}
          precision={2}
          prefix="¥"
          loading={isLoading}
          valueStyle={{ color: 'var(--danger-color)' }}
        />
      </div>

      {/* 单次查询上限提示：汇总与导出仅覆盖当前返回的 500 条 */}
      {data && data.length >= 500 && (
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          message="结果较多，仅显示最近 500 条处方"
          description="上方汇总与 CSV 导出仅覆盖当前返回的记录。如需查看更早的处方，请使用搜索关键字或日期范围缩小查询范围。"
        />
      )}

      <div className="table-card">
        {isError && (
          <QueryErrorAlert
            error={error}
            onRetry={() => refetch()}
            retrying={isFetching}
            message="加载处方历史失败"
          />
        )}
        <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }} wrap>
          <Space>
            <Input.Search
              placeholder="按患者姓名或诊断搜索"
              allowClear
              style={{ width: 260 }}
              onSearch={setKeyword}
            />
            <Space.Compact>
              {QUICK_PRESETS.map((p) => (
                <Button
                  key={p.key}
                  type={quickKey === p.key ? 'primary' : 'default'}
                  onClick={() => {
                    setDateRange(getPresetRange(p.key));
                    setQuickKey(p.key);
                  }}
                >
                  {p.label}
                </Button>
              ))}
            </Space.Compact>
            <RangePicker
              value={dateRange as [Dayjs, Dayjs] | null}
              onChange={(dates) => {
                if (dates && dates[0] && dates[1]) {
                  setDateRange([dates[0], dates[1]]);
                  // 手动选择日期后取消预设高亮
                  setQuickKey(null);
                } else {
                  setDateRange(null);
                  setQuickKey(null);
                }
              }}
              placeholder={['开始日期', '结束日期']}
            />
            {dateRange && (
              <Button
                size="small"
                onClick={() => {
                  setDateRange(null);
                  setQuickKey(null);
                }}
              >
                清除日期
              </Button>
            )}
          </Space>
          <Button
            icon={<ExportOutlined />}
            onClick={handleExportCsv}
            disabled={!data || data.length === 0}
          >
            导出 CSV
          </Button>
        </Space>
        <Table<PrescriptionWithItems>
          rowKey="id"
          loading={isLoading}
          columns={columns}
          dataSource={data}
          scroll={{ x: 990 }}
          pagination={{ pageSize: 15, showSizeChanger: true }}
          onRow={(record) => ({
            // 双击行快速打开详情，与列表页交互一致
            onDoubleClick: () => setDetail(record),
            style: { cursor: 'pointer' },
          })}
          locale={{
            emptyText: (
              <EmptyState
                title={keyword || dateRange ? '未找到匹配处方' : '暂无处方记录'}
                description={
                  keyword || dateRange
                    ? '尝试更换搜索关键字或日期范围'
                    : '系统开方后历史记录将显示在此处'
                }
              />
            ),
          }}
        />
      </div>

      <Drawer
        title={`处方详情 #${detail?.id ?? ''}`}
        open={!!detail}
        onClose={() => setDetail(null)}
        width={640}
        extra={
          detail && (
            <Space size="small">
              <Button
                size="small"
                icon={<CopyOutlined />}
                onClick={() => handleCopyToPrescription(detail)}
              >
                复制到处方
              </Button>
              <Button
                size="small"
                icon={<PrinterOutlined />}
                loading={printingId === detail.id}
                onClick={() => handlePrint(detail.id!)}
              >
                打印
              </Button>
              <Button
                size="small"
                icon={<FilePdfOutlined />}
                loading={exportingPdfId === detail.id}
                onClick={() => handleExportPdf(detail.id!)}
              >
                导出PDF
              </Button>
              <Popconfirm
                title="确认删除该处方？"
                description="将回扣库存，此操作不可撤销"
                onConfirm={() => deleteMutation.mutate(detail.id!)}
                okText="删除"
                cancelText="取消"
                okButtonProps={{ danger: true }}
              >
                <Button danger size="small">
                  删除处方
                </Button>
              </Popconfirm>
            </Space>
          )
        }
      >
        {detail && (
          <>
            <Descriptions column={2} size="small" bordered>
              <Descriptions.Item label="患者姓名" span={1}>
                {detail.patient_name}
              </Descriptions.Item>
              <Descriptions.Item label="性别" span={1}>
                {detail.patient_gender || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="年龄" span={1}>
                {detail.patient_age ?? '-'}
              </Descriptions.Item>
              <Descriptions.Item label="开方人" span={1}>
                {detail.created_by || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="总金额" span={1}>
                <Tag color="blue" style={{ borderRadius: 4 }}>
                  ¥{detail.total_amount.toFixed(2)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="诊断" span={2}>
                {detail.diagnosis || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="开方时间" span={2}>
                {detail.created_at || '-'}
              </Descriptions.Item>
            </Descriptions>
            <Title level={5} style={{ marginTop: 16 }}>
              处方明细
            </Title>
            <Table<PrescriptionItem>
              rowKey={(r) => `${r.medicine_id}`}
              size="small"
              columns={itemColumns}
              dataSource={detail.items}
              pagination={false}
              locale={{
                emptyText: <EmptyState title="无明细" description="该处方未录入药材明细" />,
              }}
              summary={(rows) => (
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0}>合计</Table.Summary.Cell>
                  <Table.Summary.Cell index={1} />
                  <Table.Summary.Cell index={2} />
                  <Table.Summary.Cell index={3} />
                  <Table.Summary.Cell index={4} align="right">
                    ¥{rows.reduce((s, r) => s + r.amount, 0).toFixed(2)}
                  </Table.Summary.Cell>
                </Table.Summary.Row>
              )}
            />
          </>
        )}
      </Drawer>
    </div>
  );
}
