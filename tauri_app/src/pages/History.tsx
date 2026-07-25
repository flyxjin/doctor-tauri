import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
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
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { CopyOutlined, DeleteOutlined, ExportOutlined, PrinterOutlined } from '@ant-design/icons';
import dayjs, { type Dayjs } from 'dayjs';
import { deletePrescription, generatePrescriptionHtml, listPrescriptions } from '@/api/tauri';
import { printHtmlInIframe } from '@/utils/print';
import type { PrescriptionItem, PrescriptionWithItems } from '@/types';
import EmptyState from '@/components/EmptyState';
import { formatError } from '@/utils/formatError';

/** sessionStorage key：用于 History → Prescription 跨页面传递待复制的处方 */
export const PRESCRIPTION_COPY_KEY = 'prescription_copy_data';

const { RangePicker } = DatePicker;
const { Title } = Typography;

export default function HistoryPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { message } = App.useApp();
  const [keyword, setKeyword] = useState('');
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [detail, setDetail] = useState<PrescriptionWithItems | null>(null);
  const [printingId, setPrintingId] = useState<number | null>(null);

  // 后端日期筛选：将日期范围传入 SQL 查询，避免拉取全量再前端过滤
  const startDate = dateRange?.[0]?.format('YYYY-MM-DD');
  const endDate = dateRange?.[1]?.format('YYYY-MM-DD');

  const { data, isLoading } = useQuery({
    queryKey: ['prescriptions', keyword, startDate, endDate],
    queryFn: () => listPrescriptions(keyword || undefined, startDate, endDate, 500),
  });

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
      setDetail(null);
    },
    onError: (e: unknown) => message.error(formatError(e)),
  });

  // 导出当前筛选结果为 CSV 并触发下载
  const handleExportCsv = () => {
    const list = data ?? [];
    if (list.length === 0) {
      message.warning('没有可导出的数据');
      return;
    }
    const header = [
      '处方号',
      '患者姓名',
      '性别',
      '年龄',
      '诊断',
      '味数',
      '金额',
      '开方人',
      '开方时间',
    ];
    const lines = [header.join(',')];
    for (const p of list) {
      const row = [
        String(p.id ?? ''),
        p.patient_name,
        p.patient_gender,
        p.patient_age != null ? String(p.patient_age) : '',
        p.diagnosis,
        String(p.items.length),
        p.total_amount.toFixed(2),
        p.created_by,
        p.created_at ?? '',
      ];
      // 用双引号包裹含逗号的字段
      const escaped = row.map((f) => {
        const s = String(f);
        if (s.includes(',') || s.includes('"') || s.includes('\n')) {
          return `"${s.replace(/"/g, '""')}"`;
        }
        return s;
      });
      lines.push(escaped.join(','));
    }
    // UTF-8 BOM，便于 Excel 正确识别中文
    const csv = '\uFEFF' + lines.join('\r\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `处方历史_${dayjs().format('YYYYMMDD_HHmmss')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    message.success(`已导出 ${list.length} 条处方记录`);
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

  /** 复制到处方：把处方头+明细存入 sessionStorage，跳转到处方页预填
   *
   * 设计要点：
   * - 沿用原方价格（复诊常沿用原价，医生可在处方页手动调整）
   * - 不复制 created_at（新处方用当前时间）
   * - 不复制 id/prescription_id/batch_id（新处方为新行）
   */
  const handleCopyToPrescription = (record: PrescriptionWithItems) => {
    const payload = {
      patient_name: record.patient_name,
      patient_age: record.patient_age ?? null,
      patient_gender: record.patient_gender,
      diagnosis: record.diagnosis,
      created_by: record.created_by,
      items: record.items.map((i) => ({
        medicine_id: i.medicine_id,
        medicine_name: i.medicine_name,
        quantity: i.quantity,
        unit: i.unit,
        price: i.price,
        amount: Number((i.quantity * i.price).toFixed(2)),
      })),
    };
    sessionStorage.setItem(PRESCRIPTION_COPY_KEY, JSON.stringify(payload));
    setDetail(null);
    navigate('/prescription');
    message.success(`已加载处方 #${record.id} 的 ${record.items.length} 味药材，请核对后保存`);
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
      width: 230,
      fixed: 'right',
      render: (_v, record) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => setDetail(record)}>
            详情
          </Button>
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopyToPrescription(record)}
          >
            复制
          </Button>
          <Button
            type="link"
            size="small"
            icon={<PrinterOutlined />}
            loading={printingId === record.id}
            onClick={() => handlePrint(record.id!)}
          >
            打印
          </Button>
          <Popconfirm
            title="确认删除该处方？"
            description="将回扣库存，此操作不可撤销"
            onConfirm={() => deleteMutation.mutate(record.id!)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
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

      {/* 汇总统计 */}
      <Space size="large" style={{ marginBottom: 16 }}>
        <Statistic title="处方数" value={summary.count} />
        <Statistic title="总味数" value={summary.totalItems} />
        <Statistic
          title="总金额"
          value={summary.totalAmount}
          precision={2}
          prefix="¥"
          valueStyle={{ color: '#cf1322' }}
        />
      </Space>

      <div className="table-card">
        <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }} wrap>
          <Space>
            <Input.Search
              placeholder="按患者姓名或诊断搜索"
              allowClear
              style={{ width: 260 }}
              onSearch={setKeyword}
            />
            <RangePicker
              value={dateRange as [Dayjs, Dayjs] | null}
              onChange={(dates) => {
                if (dates && dates[0] && dates[1]) {
                  setDateRange([dates[0], dates[1]]);
                } else {
                  setDateRange(null);
                }
              }}
              placeholder={['开始日期', '结束日期']}
            />
            {dateRange && (
              <Button size="small" onClick={() => setDateRange(null)}>
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
          scroll={{ x: 1150 }}
          pagination={{ pageSize: 15, showSizeChanger: true }}
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
