// 数据模型：与数据库表一一对应，全部实现 Serialize/Deserialize 供前后端交互
// 时间戳字段统一用 String 承载（SQLite TIMESTAMP 实际存储为 TEXT），由 chrono 在写入时格式化

use serde::{Deserialize, Serialize};

/// 药材
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Medicine {
    pub id: Option<i64>,
    pub name: String,
    #[serde(default)]
    pub alias: String,
    #[serde(default)]
    pub category: String,
    #[serde(default)]
    pub nature: String,
    #[serde(default)]
    pub taste: String,
    #[serde(default)]
    pub meridian: String,
    #[serde(default)]
    pub efficacy: String,
    #[serde(default)]
    pub indications: String,
    #[serde(default)]
    pub usage: String,
    #[serde(default)]
    pub dosage: String,
    #[serde(default)]
    pub contraindication: String,
    #[serde(default)]
    pub notes: String,
    #[serde(default)]
    pub created_at: Option<String>,
    #[serde(default)]
    pub updated_at: Option<String>,
}

/// 库存（一批次一行；列表查询时携带药材名与分类）
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Inventory {
    pub id: Option<i64>,
    pub medicine_id: i64,
    /// 批次号（空字符串表示默认批次）
    #[serde(default)]
    pub batch_no: String,
    /// 生产日期 YYYY-MM-DD（可为空）
    #[serde(default)]
    pub production_date: Option<String>,
    /// 效期 YYYY-MM-DD（可为空）
    #[serde(default)]
    pub expiry_date: Option<String>,
    #[serde(default)]
    pub quantity: f64,
    #[serde(default = "default_unit")]
    pub unit: String,
    #[serde(default)]
    pub price: f64,
    #[serde(default)]
    pub min_stock: f64,
    #[serde(default)]
    pub notes: String,
    #[serde(default)]
    pub created_at: Option<String>,
    #[serde(default)]
    pub updated_at: Option<String>,
    // 联表查询补充字段
    #[serde(default)]
    pub medicine_name: String,
    #[serde(default)]
    pub category: String,
}

fn default_unit() -> String {
    "g".to_string()
}

/// 处方
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Prescription {
    pub id: Option<i64>,
    /// 关联患者档案 id（历史数据/重名/手输姓名时为 None，仍按姓名关联）
    #[serde(default)]
    pub patient_id: Option<i64>,
    #[serde(default)]
    pub patient_name: String,
    #[serde(default)]
    pub patient_age: Option<i64>,
    #[serde(default)]
    pub patient_gender: String,
    #[serde(default)]
    pub diagnosis: String,
    #[serde(default)]
    pub total_amount: f64,
    #[serde(default)]
    pub created_by: String,
    /// 帖数（剂量倍数）：total_amount 与库存出库均按 单帖用量 × 帖数 计算，历史数据为 1
    #[serde(default = "default_dosage_count")]
    pub dosage_count: i64,
    /// 煎服法/用法说明（如"水煎服，每日一剂，分早晚两次温服"）
    #[serde(default)]
    pub usage_method: String,
    #[serde(default)]
    pub created_at: Option<String>,
}

fn default_dosage_count() -> i64 {
    1
}

/// 处方明细
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrescriptionItem {
    pub id: Option<i64>,
    #[serde(default)]
    pub prescription_id: Option<i64>,
    pub medicine_id: i64,
    pub medicine_name: String,
    #[serde(default)]
    pub quantity: f64,
    #[serde(default = "default_unit")]
    pub unit: String,
    #[serde(default)]
    pub price: f64,
    #[serde(default)]
    pub amount: f64,
    /// 扣减的批次 ID（008 迁移新增；删除处方时按此精确回扣）
    #[serde(default)]
    pub batch_id: Option<i64>,
}

/// 创建处方入参：处方头 + 明细列表
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreatePrescriptionInput {
    #[serde(flatten)]
    pub prescription: Prescription,
    pub items: Vec<PrescriptionItem>,
}

/// 处方 + 明细（历史/详情查询返回）
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrescriptionWithItems {
    #[serde(flatten)]
    pub prescription: Prescription,
    pub items: Vec<PrescriptionItem>,
}

/// 库存变更历史
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InventoryHistory {
    pub id: Option<i64>,
    pub medicine_id: i64,
    pub medicine_name: String,
    #[serde(rename = "type")]
    pub history_type: String,
    #[serde(default)]
    pub quantity: f64,
    #[serde(default)]
    pub price: Option<f64>,
    #[serde(default)]
    pub total_amount: Option<f64>,
    #[serde(default)]
    pub operator: String,
    #[serde(default)]
    pub notes: String,
    #[serde(default)]
    pub created_at: Option<String>,
    /// 关联批次 ID（008 迁移新增；按批次追溯）
    #[serde(default)]
    pub batch_id: Option<i64>,
}

/// 操作日志
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OperationLog {
    pub id: Option<i64>,
    pub operation_type: String,
    pub target_type: String,
    pub target_id: i64,
    #[serde(default)]
    pub operator: String,
    #[serde(default)]
    pub details: String,
    #[serde(default)]
    pub created_at: Option<String>,
}

// ==================== 看板与统计 ====================

/// 配伍禁忌冲突项
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompatibilityConflict {
    pub medicine1: String,
    pub medicine2: String,
    pub description: String,
}

/// 低库存项
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LowStockItem {
    pub medicine_id: i64,
    pub medicine_name: String,
    pub quantity: f64,
    pub min_stock: f64,
    pub unit: String,
}

/// 看板每日趋势（日期 + 营收 + 处方数）
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DashboardDailyTrend {
    pub date: String,
    pub revenue: f64,
    pub prescription_count: i64,
}

/// 看板数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DashboardData {
    pub medicine_count: i64,
    pub prescription_count: i64,
    pub total_stock_value: f64,
    pub low_stock_count: i64,
    pub low_stock_list: Vec<LowStockItem>,
    pub recent_prescriptions: Vec<Prescription>,
    /// 今日开方数（按本地日期匹配）
    pub today_prescription_count: i64,
    /// 今日销售收入（按本地日期匹配）
    pub today_revenue: f64,
    /// 近 7 天每日营收与处方数趋势
    pub daily_trend: Vec<DashboardDailyTrend>,
}

/// 统计卡片
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StatisticsSummary {
    pub prescription_count: i64,
    pub total_amount: f64,
    pub medicine_kinds: i64,
    pub avg_amount: f64,
}

/// 热销药材 TOP
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TopMedicine {
    pub medicine_name: String,
    pub total_quantity: f64,
    pub total_amount: f64,
}

/// 按日趋势
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DailyTrend {
    pub date: String,
    pub prescription_count: i64,
    pub total_amount: f64,
}

/// 统计数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StatisticsData {
    pub summary: StatisticsSummary,
    pub top_medicines: Vec<TopMedicine>,
    pub daily_trend: Vec<DailyTrend>,
}

// ==================== 批量导入 / 导出 ====================

/// 批量导入药材记录（前端传入的每行数据）
///
/// 数值字段使用 Option<String>，Rust 端做类型转换保护，避免脏数据导致整批失败
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MedicineImportRecord {
    pub name: String,
    #[serde(default)]
    pub alias: String,
    #[serde(default)]
    pub category: String,
    #[serde(default)]
    pub nature: String,
    #[serde(default)]
    pub taste: String,
    #[serde(default)]
    pub meridian: String,
    #[serde(default)]
    pub efficacy: String,
    #[serde(default)]
    pub indications: String,
    #[serde(default)]
    pub usage: String,
    #[serde(default)]
    pub dosage: String,
    #[serde(default)]
    pub contraindication: String,
    #[serde(default)]
    pub notes: String,
    /// 数值字段以字符串接收，由后端做 try_parse，保留原始数据用于错误提示
    #[serde(default)]
    pub quantity: Option<String>,
    #[serde(default)]
    pub unit: String,
    #[serde(default)]
    pub price: Option<String>,
    #[serde(default)]
    pub min_stock: Option<String>,
}

/// 批量导入结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BatchImportResult {
    pub inserted: u32,
    pub updated: u32,
    pub errors: Vec<String>,
}

// ==================== 批次与效期 ====================

/// 效期预警批次
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExpiringBatch {
    pub id: i64,
    pub medicine_id: i64,
    pub medicine_name: String,
    pub batch_no: String,
    pub expiry_date: String,
    pub quantity: f64,
    pub unit: String,
    pub price: f64,
}

// ==================== 自动更新 ====================

/// Gitee Release 解析后的更新信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateInfo {
    pub version: String,
    pub release_name: String,
    pub changelog: String,
    pub download_url: String,
    pub file_size: u64,
    /// 安装包 SHA256（十六进制小写），来自 Release 附带的 `.sha256` 侧车文件；
    /// 旧版 Release 无此文件时为空串，此时跳过哈希校验（仅做大小校验）
    pub checksum: String,
}

/// 下载进度（通过 Channel 推送给前端）
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DownloadProgress {
    pub downloaded: u64,
    pub total: u64,
}

/// 启动时静默检查 + 下载的结果
///
/// - `has_update=true` 且 `downloaded_path` 非空：已下载完成，前端弹窗引导用户立即安装
/// - `has_update=true` 且 `downloaded_path` 为空：发现新版本但下载失败或无 .exe 资源，
///   前端可引导用户到 Settings 页手动重试
/// - `has_update=false`：当前已是最新版本
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SilentUpdateResult {
    pub has_update: bool,
    pub info: UpdateInfo,
    /// 已下载到本地的安装包路径；空字符串表示未下载
    #[serde(default)]
    pub downloaded_path: String,
}

// ==================== 数据备份与恢复 ====================

/// 单次备份结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackupInfo {
    pub backup_path: String,
    pub file_size: u64,
    pub checksum: String,
    pub created_at: String,
}

/// 备份列表项
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackupEntry {
    pub backup_path: String,
    pub file_size: u64,
    pub checksum: String,
    pub created_at: String,
}

// ==================== 客户管理（患者档案） ====================

/// 患者档案
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Patient {
    pub id: Option<i64>,
    pub name: String,
    #[serde(default)]
    pub gender: String,
    #[serde(default)]
    pub age: Option<i64>,
    #[serde(default)]
    pub phone: String,
    #[serde(default)]
    pub address: String,
    #[serde(default)]
    pub allergy: String,
    #[serde(default)]
    pub medical_history: String,
    #[serde(default)]
    pub notes: String,
    #[serde(default)]
    pub created_at: String,
    #[serde(default)]
    pub updated_at: String,
}

/// 患者统计数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PatientStatistics {
    pub prescription_count: i64,
    pub total_amount: f64,
    pub first_visit: Option<String>,
    pub last_visit: Option<String>,
}
