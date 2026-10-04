// Tauri invoke 封装：所有后端命令调用集中于此
// 后端命令返回 Result<T, String>，此处统一抛出 Error 供 TanStack Query 捕获

import { invoke, Channel } from '@tauri-apps/api/core';
import type {
  AppSetting,
  BackupEntry,
  BackupInfo,
  BatchImportResult,
  CompatibilityConflict,
  CreatePrescriptionInput,
  DashboardData,
  DoctorStat,
  DownloadProgress,
  ExpiringBatch,
  Inventory,
  InventoryHistory,
  Medicine,
  MedicineImportRecord,
  MyTemplate,
  OperationLog,
  Patient,
  PatientStatistics,
  PrescriptionWithItems,
  SilentUpdateResult,
  StatisticsData,
  UpdateInfo,
} from '@/types';

/** 药材列表（支持关键字、分类与药性筛选） */
export async function listMedicines(
  keyword?: string,
  category?: string,
  nature?: string,
): Promise<Medicine[]> {
  return invoke<Medicine[]>('list_medicines', { keyword, category, nature });
}

/** 新增药材，返回新 ID */
export async function createMedicine(medicine: Medicine): Promise<number> {
  return invoke<number>('create_medicine', { medicine });
}

/** 更新药材 */
export async function updateMedicine(medicine: Medicine): Promise<void> {
  return invoke<void>('update_medicine', { medicine });
}

/** 删除药材 */
export async function deleteMedicine(id: number): Promise<void> {
  return invoke<void>('delete_medicine', { id });
}

/** 库存列表 */
export async function listInventory(): Promise<Inventory[]> {
  return invoke<Inventory[]>('list_inventory');
}

/**
 * 库存调整：将指定批次库存设置为目标数量
 *
 * 用于盘点场景，差值自动记入变更历史
 */
export async function adjustStock(
  inventoryId: number,
  targetQuantity: number,
  operator?: string,
  notes?: string,
): Promise<void> {
  return invoke<void>('adjust_stock', {
    inventoryId,
    targetQuantity,
    operator,
    notes,
  });
}

/** 修改单个库存批次单价（库存页行内改价），记操作日志 */
export async function updateInventoryPrice(
  inventoryId: number,
  price: number,
  operator?: string,
): Promise<void> {
  return invoke<void>('update_inventory_price', { inventoryId, price, operator });
}

/**
 * 按药材分类批量调价（v1.10.0）
 *
 * @param mode "set"（设为固定单价）| "percent"（按现价上下浮动百分比）
 * @returns 受影响的批次数量
 */
export async function batchUpdatePrice(
  category: string,
  mode: 'set' | 'percent',
  value: number,
  operator?: string,
): Promise<number> {
  return invoke<number>('batch_update_price', { category, mode, value, operator });
}

/**
 * 入库 / 出库（批次版，008 迁移）
 *
 * - `is_in=true` 入库：`batchNo`/`productionDate`/`expiryDate` 生效；同批次号自动合并，新批次号新建行
 * - `is_in=false` 出库：忽略批次参数，按 FEFO（近效期优先）跨批次扣减
 */
export async function updateStock(
  medicineId: number,
  change: number,
  isIn: boolean,
  operator?: string,
  notes?: string,
  batchNo?: string,
  productionDate?: string,
  expiryDate?: string,
): Promise<void> {
  return invoke<void>('update_stock', {
    medicineId,
    change,
    isIn,
    operator,
    notes,
    batchNo,
    productionDate,
    expiryDate,
  });
}

/** 效期预警：查询指定天数内到期的批次（默认 30 天） */
export async function listExpiringBatches(days?: number): Promise<ExpiringBatch[]> {
  return invoke<ExpiringBatch[]>('list_expiring_batches', { days });
}

/** 库存变更历史（支持按药材、类型、日期范围筛选） */
export async function listInventoryHistory(
  medicineId?: number,
  historyType?: string,
  startDate?: string,
  endDate?: string,
  limit?: number,
): Promise<InventoryHistory[]> {
  return invoke<InventoryHistory[]>('list_inventory_history', {
    medicineId,
    historyType,
    startDate,
    endDate,
    limit,
  });
}

/** 处方历史列表（含明细，支持关键字与日期范围筛选） */
export async function listPrescriptions(
  keyword?: string,
  startDate?: string,
  endDate?: string,
  limit?: number,
): Promise<PrescriptionWithItems[]> {
  return invoke<PrescriptionWithItems[]>('list_prescriptions', {
    keyword,
    startDate,
    endDate,
    limit,
  });
}

/** 创建处方，返回新处方 ID */
export async function createPrescription(
  input: CreatePrescriptionInput,
): Promise<number> {
  return invoke<number>('create_prescription', { input });
}

/** 删除处方 */
export async function deletePrescription(id: number): Promise<void> {
  return invoke<void>('delete_prescription', { id });
}

/** 首页看板数据 */
export async function getDashboardData(): Promise<DashboardData> {
  return invoke<DashboardData>('get_dashboard_data');
}

/** 销售统计（按时间范围，格式 YYYY-MM-DD） */
export async function getStatistics(
  startDate: string,
  endDate: string,
): Promise<StatisticsData> {
  return invoke<StatisticsData>('get_statistics', {
    startDate,
    endDate,
  });
}

/** 医师开方量统计：按开方人聚合的处方数与金额（指定日期区间） */
export async function getDoctorStats(
  startDate: string,
  endDate: string,
): Promise<DoctorStat[]> {
  return invoke<DoctorStat[]>('get_doctor_stats', {
    startDate,
    endDate,
  });
}

/** 配伍禁忌检查（十八反、十九畏） */
export async function checkCompatibility(
  medicineNames: string[],
): Promise<CompatibilityConflict[]> {
  return invoke<CompatibilityConflict[]>('check_compatibility', {
    medicineNames,
  });
}

// ==================== 批量导入 / 导出 ====================

/** 批量导入药材：事务内 UPSERT */
export async function batchImportMedicines(
  records: MedicineImportRecord[],
): Promise<BatchImportResult> {
  return invoke<BatchImportResult>('batch_import_medicines', { records });
}

/** 导出全量药材为 CSV 字符串（UTF-8 with BOM） */
export async function exportMedicinesCsv(): Promise<string> {
  return invoke<string>('export_medicines_csv');
}

/** 下载导入模板（含 2 条样本数据） */
export async function downloadImportTemplate(): Promise<string> {
  return invoke<string>('download_import_template');
}

/** 把字符串内容写入下载目录并返回绝对路径 */
export async function saveTextToDownloads(
  filename: string,
  content: string,
): Promise<string> {
  return invoke<string>('save_text_to_downloads', { filename, content });
}

/** 操作日志查询（支持按操作类型、目标类型、日期范围筛选） */
export async function listOperationLogs(
  operationType?: string,
  targetType?: string,
  startDate?: string,
  endDate?: string,
  limit?: number,
): Promise<OperationLog[]> {
  return invoke<OperationLog[]>('list_operation_logs', {
    operationType,
    targetType,
    startDate,
    endDate,
    limit,
  });
}

// ==================== 打印处方 ====================

/** 生成处方 HTML 字符串（含患者信息、药材表格、总金额） */
export async function generatePrescriptionHtml(
  prescriptionId: number,
): Promise<string> {
  return invoke<string>('generate_prescription_html', { prescriptionId });
}

// ==================== 客户管理（患者档案） ====================

/** 患者列表（支持按姓名/电话搜索） */
export async function listPatients(keyword?: string): Promise<Patient[]> {
  return invoke<Patient[]>('list_patients', { keyword: keyword ?? null });
}

/** 新增患者档案，返回新 ID */
export async function createPatient(patient: Patient): Promise<number> {
  return invoke<number>('create_patient', { patient });
}

/** 更新患者档案 */
export async function updatePatient(patient: Patient): Promise<void> {
  return invoke<void>('update_patient', { patient });
}

/** 删除患者档案 */
export async function deletePatient(id: number): Promise<void> {
  return invoke<void>('delete_patient', { id });
}

/** 患者统计数据：处方数、总金额、首诊/末诊日期（id 关联 + 姓名兜底匹配历史数据） */
export async function getPatientStatistics(
  id: number,
  name: string,
): Promise<PatientStatistics> {
  return invoke<PatientStatistics>('get_patient_statistics', { id, name });
}

// ==================== 应用设置与我的方剂 ====================

/** 读取全部应用设置（诊所抬头等） */
export async function getAppSettings(): Promise<AppSetting[]> {
  return invoke<AppSetting[]>('get_app_settings');
}

/** 写入单个应用设置 */
export async function setAppSetting(key: string, value: string): Promise<void> {
  return invoke<void>('set_app_setting', { key, value });
}

/** 我的方剂列表 */
export async function listMyTemplates(): Promise<MyTemplate[]> {
  return invoke<MyTemplate[]>('list_my_templates');
}

/** 保存我的方剂（同名覆盖），返回模板 id */
export async function saveMyTemplate(
  name: string,
  description: string,
  indication: string,
  itemsJson: string,
): Promise<number> {
  return invoke<number>('save_my_template', {
    name,
    description,
    indication,
    itemsJson,
  });
}

/** 删除我的方剂 */
export async function deleteMyTemplate(id: number): Promise<void> {
  return invoke<void>('delete_my_template', { id });
}

// ==================== 数据备份与恢复 ====================

/** 创建数据库备份 */
export async function createBackup(): Promise<BackupInfo> {
  return invoke<BackupInfo>('create_backup');
}

/** 列出所有备份（按时间倒序） */
export async function listBackups(): Promise<BackupEntry[]> {
  return invoke<BackupEntry[]>('list_backups');
}

/** 基于备份还原数据库 */
export async function restoreBackup(backupPath: string): Promise<void> {
  return invoke<void>('restore_backup', { backupPath });
}

/** 删除指定备份文件及其清单 */
export async function deleteBackup(backupPath: string): Promise<void> {
  return invoke<void>('delete_backup', { backupPath });
}

// ==================== 自动更新 ====================

/** 检查 Gitee 最新 Release */
export async function checkForUpdate(): Promise<UpdateInfo> {
  return invoke<UpdateInfo>('check_for_update');
}

/**
 * 下载更新到下载目录，返回本地路径。
 * 通过 Channel 接收下载进度。
 *
 * @param url 下载地址（来自 checkForUpdate 返回的 download_url）
 * @param fileSize 文件大小（来自 checkForUpdate 返回的 file_size，用于完整性校验）
 * @param checksum 安装包 SHA256（来自 checkForUpdate 返回的 checksum，可为空）
 * @param onProgress 下载进度回调
 */
export async function downloadUpdate(
  url: string,
  fileSize: number,
  checksum: string,
  onProgress: (progress: DownloadProgress) => void,
): Promise<string> {
  const channel = new Channel<DownloadProgress>();
  channel.onmessage = onProgress;
  return invoke<string>('download_update', { url, fileSize, checksum, onProgress: channel });
}

/** 启动下载好的安装程序 */
export async function installUpdate(
  exePath: string,
  silent?: boolean,
): Promise<void> {
  return invoke<void>('install_update', { exePath, silent });
}

/**
 * 启动时后台静默检查 + 下载
 *
 * - 内部完成版本比较，仅当 `remote > currentVersion` 时下载
 * - 下载失败时 `has_update=true` 但 `downloaded_path` 为空，前端可降级到手动重试
 * - 网络错误等异常会以 reject 形式抛出，前端需 try/catch
 */
export async function checkAndDownloadSilently(
  currentVersion: string,
): Promise<SilentUpdateResult> {
  return invoke<SilentUpdateResult>('check_and_download_silently', {
    currentVersion,
  });
}
