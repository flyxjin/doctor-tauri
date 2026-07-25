// CSV 导出统一 Hook
//
// 抽取自 Statistics / Patients / MedicineList / Inventory / History 五个页面中
// 重复的"空数据检查 + rowsToCsv + saveTextToDownloads + message 提示"流程。
//
// 统一了原本 4 种不一致的变体：
// - 保存机制：统一用 saveTextToDownloads（写入系统下载目录并返回路径）
// - 时间戳格式：统一 YYYYMMDD_HHmmss（避免同日多次导出被覆盖）
// - 行分隔符：统一 \r\n（Excel 友好）
// - 成功提示：统一"已导出 N 条 X 到：path"

import { App } from 'antd';
import dayjs from 'dayjs';
import { saveTextToDownloads } from '@/api/tauri';
import { rowsToCsv } from '@/utils/csv';
import { formatError } from '@/utils/formatError';

/** CSV 行单元格类型 */
export type CsvRow = (string | number | null | undefined)[];

export interface UseCsvExportOptions {
  /** 文件名前缀（不含时间戳与扩展名），例如 'patients_export' */
  filenamePrefix: string;
  /** 成功提示中描述导出内容的文案，例如 '患者档案' / '药材记录' */
  label?: string;
}

export interface UseCsvExportResult {
  /**
   * 导出 CSV 到下载目录。
   *
   * @param rows 二维数组，第一行通常为表头
   * @param count 可选的数据条数，用于成功提示；不传则不显示条数
   */
  exportCsv: (rows: CsvRow[], count?: number) => Promise<void>;
}

/**
 * CSV 导出 Hook：统一封装时间戳生成、文件保存、错误处理与用户提示。
 *
 * 调用方只需负责构建 rows（含表头），其余交给本 hook。
 */
export function useCsvExport(options: UseCsvExportOptions): UseCsvExportResult {
  const { message } = App.useApp();
  const { filenamePrefix, label } = options;

  const exportCsv = async (rows: CsvRow[], count?: number) => {
    if (rows.length <= 1) {
      // 只有表头或完全为空
      message.warning('没有可导出的数据');
      return;
    }
    const csv = rowsToCsv(rows);
    try {
      const ts = dayjs().format('YYYYMMDD_HHmmss');
      const path = await saveTextToDownloads(`${filenamePrefix}_${ts}.csv`, csv);
      const countPart = count != null ? `${count} 条` : '';
      const labelPart = label ?? '';
      const sep = countPart && labelPart ? ' ' : '';
      message.success(`已导出 ${countPart}${sep}${labelPart}到：${path}`.replace(/\s+/g, ' ').trim());
    } catch (e) {
      message.error(formatError(e));
    }
  };

  return { exportCsv };
}
