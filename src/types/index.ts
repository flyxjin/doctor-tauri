// TypeScript 类型定义：与 Rust src/models.rs 一一对应

export interface Medicine {
  id: number | null;
  name: string;
  alias?: string;
  category?: string;
  nature?: string;
  taste?: string;
  meridian?: string;
  efficacy?: string;
  indications?: string;
  usage?: string;
  dosage?: string;
  contraindication?: string;
  notes?: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface Inventory {
  id: number | null;
  medicine_id: number;
  /** 批次号（008 迁移新增；空字符串表示默认批次） */
  batch_no: string;
  /** 生产日期 YYYY-MM-DD（可为空） */
  production_date?: string | null;
  /** 效期 YYYY-MM-DD（可为空） */
  expiry_date?: string | null;
  quantity: number;
  unit: string;
  price: number;
  min_stock: number;
  notes?: string;
  created_at?: string | null;
  updated_at?: string | null;
  // 联表补充字段
  medicine_name?: string;
  category?: string;
}

export interface Prescription {
  id: number | null;
  patient_name: string;
  patient_age?: number | null;
  patient_gender: string;
  diagnosis: string;
  total_amount: number;
  created_by: string;
  created_at?: string | null;
}

export interface PrescriptionItem {
  id?: number | null;
  prescription_id?: number | null;
  medicine_id: number;
  medicine_name: string;
  quantity: number;
  unit: string;
  price: number;
  amount: number;
  /** 扣减的批次 ID（008 迁移新增；删除处方时按此精确回扣） */
  batch_id?: number | null;
}

export interface CreatePrescriptionInput extends Prescription {
  items: PrescriptionItem[];
}

export interface PrescriptionWithItems extends Prescription {
  items: PrescriptionItem[];
}

export interface InventoryHistory {
  id: number | null;
  medicine_id: number;
  medicine_name: string;
  type: string;
  quantity: number;
  price?: number | null;
  total_amount?: number | null;
  operator?: string;
  notes?: string;
  created_at?: string | null;
  /** 关联批次 ID（008 迁移新增；按批次追溯） */
  batch_id?: number | null;
}

/** 效期预警批次（008 迁移新增） */
export interface ExpiringBatch {
  id: number;
  medicine_id: number;
  medicine_name: string;
  batch_no: string;
  expiry_date: string;
  quantity: number;
  unit: string;
  price: number;
}

export interface OperationLog {
  id: number | null;
  operation_type: string;
  target_type: string;
  target_id: number;
  operator?: string;
  details?: string;
  created_at?: string | null;
}

// ==================== 看板与统计 ====================

export interface CompatibilityConflict {
  medicine1: string;
  medicine2: string;
  description: string;
}

export interface LowStockItem {
  medicine_id: number;
  medicine_name: string;
  quantity: number;
  min_stock: number;
  unit: string;
}

export interface DashboardData {
  medicine_count: number;
  prescription_count: number;
  total_stock_value: number;
  low_stock_count: number;
  low_stock_list: LowStockItem[];
  recent_prescriptions: Prescription[];
}

export interface StatisticsSummary {
  prescription_count: number;
  total_amount: number;
  medicine_kinds: number;
  avg_amount: number;
}

export interface TopMedicine {
  medicine_name: string;
  total_quantity: number;
  total_amount: number;
}

export interface DailyTrend {
  date: string;
  prescription_count: number;
  total_amount: number;
}

export interface StatisticsData {
  summary: StatisticsSummary;
  top_medicines: TopMedicine[];
  daily_trend: DailyTrend[];
}

// ==================== 批量导入 / 导出 ====================

/** 批量导入药材记录（与 Rust MedicineImportRecord 对齐） */
export interface MedicineImportRecord {
  name: string;
  alias?: string;
  category?: string;
  nature?: string;
  taste?: string;
  meridian?: string;
  efficacy?: string;
  indications?: string;
  usage?: string;
  dosage?: string;
  contraindication?: string;
  notes?: string;
  /** 数值字段以字符串形式接收，Rust 端做 try_parse */
  quantity?: string;
  unit?: string;
  price?: string;
  min_stock?: string;
}

/** 批量导入结果 */
export interface BatchImportResult {
  inserted: number;
  updated: number;
  errors: string[];
}

// ==================== 自动更新 ====================

/** Gitee Release 解析后的更新信息 */
export interface UpdateInfo {
  version: string;
  release_name: string;
  changelog: string;
  download_url: string;
  file_size: number;
}

/** 下载进度（由 Channel 推送） */
export interface DownloadProgress {
  downloaded: number;
  total: number;
}

/**
 * 启动时静默检查 + 下载的结果
 *
 * - `has_update=true` 且 `downloaded_path` 非空：已下载完成，前端弹窗引导用户立即安装
 * - `has_update=true` 且 `downloaded_path` 为空：发现新版本但下载失败或无 .exe 资源
 * - `has_update=false`：当前已是最新版本
 */
export interface SilentUpdateResult {
  has_update: boolean;
  info: UpdateInfo;
  /** 已下载到本地的安装包路径；空字符串表示未下载 */
  downloaded_path: string;
}

// ==================== 数据备份与恢复 ====================

/** 单次备份结果 */
export interface BackupInfo {
  backup_path: string;
  file_size: number;
  md5: string;
  created_at: string;
}

/** 备份列表项 */
export interface BackupEntry {
  backup_path: string;
  file_size: number;
  md5: string;
  created_at: string;
}

// ==================== 客户管理（患者档案） ====================

/** 患者档案（与 Rust Patient 对齐） */
export interface Patient {
  id: number | null;
  name: string;
  gender?: string;
  age?: number | null;
  phone?: string;
  address?: string;
  allergy?: string;
  medical_history?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

/** 患者统计数据（与 Rust PatientStatistics 对齐） */
export interface PatientStatistics {
  prescription_count: number;
  total_amount: number;
  first_visit?: string | null;
  last_visit?: string | null;
}
