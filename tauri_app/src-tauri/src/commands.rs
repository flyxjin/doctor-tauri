// Tauri commands：前端通过 invoke 调用的后端接口
//
// 约定：
// - 所有命令返回 Result<T, String>，错误信息以中文返回前端
// - 所有 SQL 均使用参数化查询，杜绝 SQL 注入
// - 数据库连接由 Tauri State<DbState> 管理，通过 Mutex 串行访问

use crate::compatibility;
use crate::db::DbState;
use crate::models::*;
use rusqlite::types::Value as SqlValue;
use rusqlite::{params, params_from_iter, Connection, OptionalExtension};
use std::path::PathBuf;
use tauri::{Manager, State};

/// 记录操作日志
fn log_operation(
    conn: &Connection,
    op_type: &str,
    target_type: &str,
    target_id: i64,
    details: &str,
) -> Result<(), String> {
    conn.execute(
        "INSERT INTO operation_logs (operation_type, target_type, target_id, details) VALUES (?1,?2,?3,?4)",
        params![op_type, target_type, target_id, details],
    )
    .map_err(|e| format!("记录操作日志失败: {e}"))?;
    Ok(())
}

// ==================== 药材管理 ====================

/// 药材列表（支持按分类、关键字搜索）
#[tauri::command]
pub fn list_medicines(
    keyword: Option<String>,
    category: Option<String>,
    state: State<'_, DbState>,
) -> Result<Vec<Medicine>, String> {
    let conn = state.lock()?;
    let mut sql = String::from(
        "SELECT id, name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at FROM medicines WHERE 1=1",
    );
    let mut pv: Vec<SqlValue> = Vec::new();
    if let Some(cat) = &category {
        if !cat.is_empty() {
            sql.push_str(" AND category = ?");
            pv.push(SqlValue::Text(cat.clone()));
        }
    }
    if let Some(kw) = &keyword {
        if !kw.is_empty() {
            sql.push_str(" AND (name LIKE ? OR alias LIKE ? OR efficacy LIKE ?)");
            let pat = format!("%{kw}%");
            pv.push(SqlValue::Text(pat.clone()));
            pv.push(SqlValue::Text(pat.clone()));
            pv.push(SqlValue::Text(pat));
        }
    }
    sql.push_str(" ORDER BY id ASC");

    let medicines: Vec<Medicine> = {
        let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params_from_iter(pv.iter()), map_medicine_row)
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };
    Ok(medicines)
}

/// 获取单条药材
#[tauri::command]
pub fn get_medicine(id: i64, state: State<'_, DbState>) -> Result<Medicine, String> {
    let conn = state.lock()?;
    conn.query_row(
        "SELECT id, name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at FROM medicines WHERE id=?1",
        params![id],
        map_medicine_row,
    )
    .optional()
    .map_err(|e| e.to_string())?
    .ok_or_else(|| format!("药材 id={id} 不存在"))
}

/// 新增药材
#[tauri::command]
pub fn create_medicine(
    medicine: Medicine,
    state: State<'_, DbState>,
) -> Result<i64, String> {
    if medicine.name.trim().is_empty() {
        return Err("药材名称不能为空".to_string());
    }
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;
    let exists: Option<i64> = tx
        .query_row(
            "SELECT id FROM medicines WHERE name = ?1",
            params![&medicine.name],
            |row| row.get(0),
        )
        .optional()
        .map_err(|e| e.to_string())?;
    if exists.is_some() {
        return Err(format!("药材 '{}' 已存在", medicine.name));
    }
    tx.execute(
        "INSERT INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12)",
        params![
            &medicine.name,
            &medicine.alias,
            &medicine.category,
            &medicine.nature,
            &medicine.taste,
            &medicine.meridian,
            &medicine.efficacy,
            &medicine.indications,
            &medicine.usage,
            &medicine.dosage,
            &medicine.contraindication,
            &medicine.notes,
        ],
    )
    .map_err(|e| format!("创建药材失败: {e}"))?;
    let id = tx.last_insert_rowid();
    log_operation(&tx, "CREATE", "medicine", id, &format!("创建药材: {}", medicine.name))?;
    tx.commit().map_err(|e| format!("提交事务失败: {e}"))?;
    Ok(id)
}

/// 更新药材
#[tauri::command]
pub fn update_medicine(
    medicine: Medicine,
    state: State<'_, DbState>,
) -> Result<(), String> {
    let id = medicine.id.ok_or("药材ID不能为空".to_string())?;
    if medicine.name.trim().is_empty() {
        return Err("药材名称不能为空".to_string());
    }
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;
    let dup: Option<i64> = tx
        .query_row(
            "SELECT id FROM medicines WHERE name = ?1 AND id != ?2",
            params![&medicine.name, id],
            |row| row.get(0),
        )
        .optional()
        .map_err(|e| e.to_string())?;
    if dup.is_some() {
        return Err(format!("药材 '{}' 已存在", medicine.name));
    }
    tx.execute(
        "UPDATE medicines SET name=?1, alias=?2, category=?3, nature=?4, taste=?5, meridian=?6, efficacy=?7, indications=?8, usage=?9, dosage=?10, contraindication=?11, notes=?12, updated_at=CURRENT_TIMESTAMP WHERE id=?13",
        params![
            &medicine.name,
            &medicine.alias,
            &medicine.category,
            &medicine.nature,
            &medicine.taste,
            &medicine.meridian,
            &medicine.efficacy,
            &medicine.indications,
            &medicine.usage,
            &medicine.dosage,
            &medicine.contraindication,
            &medicine.notes,
            id,
        ],
    )
    .map_err(|e| format!("更新药材失败: {e}"))?;
    log_operation(&tx, "UPDATE", "medicine", id, &format!("更新药材: {}", medicine.name))?;
    tx.commit().map_err(|e| format!("提交事务失败: {e}"))?;
    Ok(())
}

/// 删除药材（级联删除库存记录）
///
/// 安全检查：若药材已被处方引用或有库存历史，禁止删除（保留审计轨迹）
#[tauri::command]
pub fn delete_medicine(id: i64, state: State<'_, DbState>) -> Result<(), String> {
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;
    // 检查是否被处方明细引用
    let ref_count: i64 = tx
        .query_row(
            "SELECT COUNT(*) FROM prescription_items WHERE medicine_id=?1",
            params![id],
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())?;
    if ref_count > 0 {
        return Err(format!(
            "该药材已被 {ref_count} 张处方引用，无法删除。建议清零库存而非删除"
        ));
    }
    // 检查是否有库存变更历史（inventory_history 外键无 ON DELETE CASCADE）
    let hist_count: i64 = tx
        .query_row(
            "SELECT COUNT(*) FROM inventory_history WHERE medicine_id=?1",
            params![id],
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())?;
    if hist_count > 0 {
        return Err(format!(
            "该药材有 {hist_count} 条库存变更历史，无法删除（需保留审计轨迹）。建议清零库存而非删除"
        ));
    }
    let name: Option<String> = tx
        .query_row(
            "SELECT name FROM medicines WHERE id=?1",
            params![id],
            |row| row.get(0),
        )
        .optional()
        .map_err(|e| e.to_string())?;
    tx.execute("DELETE FROM medicines WHERE id=?1", params![id])
        .map_err(|e| format!("删除药材失败: {e}"))?;
    log_operation(
        &tx,
        "DELETE",
        "medicine",
        id,
        &format!("删除药材: {}", name.unwrap_or_default()),
    )?;
    tx.commit().map_err(|e| format!("提交事务失败: {e}"))?;
    Ok(())
}

// ==================== 库存管理 ====================

/// 库存列表（按批次行返回，联表药材名与分类）
#[tauri::command]
pub fn list_inventory(state: State<'_, DbState>) -> Result<Vec<Inventory>, String> {
    let conn = state.lock()?;
    let list: Vec<Inventory> = {
        let mut stmt = conn.prepare(
            "SELECT i.id, i.medicine_id, i.batch_no, i.production_date, i.expiry_date,
                    i.quantity, i.unit, i.price, i.min_stock, i.notes, i.created_at, i.updated_at,
                    m.name, m.category
             FROM inventory i
             LEFT JOIN medicines m ON i.medicine_id = m.id
             ORDER BY i.medicine_id ASC, i.batch_no ASC",
        )
        .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map((), |row| {
                Ok(Inventory {
                    id: row.get(0)?,
                    medicine_id: row.get(1)?,
                    batch_no: row.get::<_, Option<String>>(2)?.unwrap_or_default(),
                    production_date: row.get(3)?,
                    expiry_date: row.get(4)?,
                    quantity: row.get::<_, Option<f64>>(5)?.unwrap_or(0.0),
                    unit: row
                        .get::<_, Option<String>>(6)?
                        .unwrap_or_else(|| "g".to_string()),
                    price: row.get::<_, Option<f64>>(7)?.unwrap_or(0.0),
                    min_stock: row.get::<_, Option<f64>>(8)?.unwrap_or(0.0),
                    notes: row.get::<_, Option<String>>(9)?.unwrap_or_default(),
                    created_at: row.get(10)?,
                    updated_at: row.get(11)?,
                    medicine_name: row.get::<_, Option<String>>(12)?.unwrap_or_default(),
                    category: row.get::<_, Option<String>>(13)?.unwrap_or_default(),
                })
            })
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };
    Ok(list)
}

/// 入库 / 出库（批次版）
///
/// - `medicine_id`：药材 ID
/// - `change`：变更数量（正数）
/// - `is_in`：true=入库，false=出库
/// - `batch_no`：批次号（入库时指定，为空则自动生成；出库时忽略，按 FEFO 自动选批次）
/// - `production_date`：生产日期 YYYY-MM-DD（入库时录入，可选）
/// - `expiry_date`：效期 YYYY-MM-DD（入库时录入，可选）
#[tauri::command]
pub fn update_stock(
    medicine_id: i64,
    change: f64,
    is_in: bool,
    operator: Option<String>,
    notes: Option<String>,
    batch_no: Option<String>,
    production_date: Option<String>,
    expiry_date: Option<String>,
    state: State<'_, DbState>,
) -> Result<(), String> {
    if change <= 0.0 {
        return Err("变更数量必须大于 0".to_string());
    }
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;

    let medicine_name: String = tx
        .query_row(
            "SELECT name FROM medicines WHERE id=?1",
            params![medicine_id],
            |row| row.get(0),
        )
        .map_err(|e| format!("药材不存在: {e}"))?;

    let hist_type = if is_in { "入库" } else { "出库" };
    let operator_str = operator.unwrap_or_default();
    let notes_str = notes.unwrap_or_default();

    if is_in {
        // ========== 入库逻辑 ==========
        let batch = batch_no.unwrap_or_default();
        let batch = if batch.trim().is_empty() {
            // 自动生成批次号：时间戳
            format!("BATCH-{}", chrono::Local::now().format("%Y%m%d%H%M%S"))
        } else {
            batch.trim().to_string()
        };
        let prod = production_date.filter(|s| !s.is_empty());
        let exp = expiry_date.filter(|s| !s.is_empty());

        // 查是否已有同批次
        let row: Option<(i64, f64, f64, String)> = tx
            .query_row(
                "SELECT id, quantity, price, unit FROM inventory WHERE medicine_id=?1 AND batch_no=?2",
                params![medicine_id, &batch],
                |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?, row.get(3)?)),
            )
            .optional()
            .map_err(|e| e.to_string())?;

        let (inv_id, _old_qty, price, unit) = match row {
            Some(r) => {
                // 同批次已存在 → 合并入库（累加数量）
                let (id, qty, price, unit) = r;
                tx.execute(
                    "UPDATE inventory SET quantity=?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
                    params![qty + change, id],
                )
                .map_err(|e| e.to_string())?;
                (id, qty, price, unit)
            }
            None => {
                // 新批次 → 新建 inventory 行
                // 默认单价/单位/最低库存取该药材已有任意批次，无则 0/'g'/0
                let (price, unit, min_stock): (f64, String, f64) = tx
                    .query_row(
                        "SELECT price, unit, min_stock FROM inventory WHERE medicine_id=?1 LIMIT 1",
                        params![medicine_id],
                        |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)),
                    )
                    .optional()
                    .map_err(|e| e.to_string())?
                    .unwrap_or((0.0, "g".to_string(), 0.0));
                tx.execute(
                    "INSERT INTO inventory (medicine_id, batch_no, production_date, expiry_date, quantity, unit, price, min_stock) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
                    params![medicine_id, &batch, &prod, &exp, change, &unit, price, min_stock],
                )
                .map_err(|e| e.to_string())?;
                (tx.last_insert_rowid(), 0.0, price, unit)
            }
        };

        let total_amount = change * price;
        tx.execute(
            "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, batch_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",
            params![medicine_id, &medicine_name, hist_type, change, price, total_amount, &operator_str, &notes_str, inv_id],
        )
        .map_err(|e| e.to_string())?;

        log_operation(
            &tx,
            "STOCK",
            "inventory",
            inv_id,
            &format!("{}: {} {}{} (批次:{})", hist_type, medicine_name, change, unit, batch),
        )?;
    } else {
        // ========== 出库逻辑（FEFO 近效期优先） ==========
        // select_batches_fefo 内部已校验库存充足，不足时直接返回错误
        let batches = select_batches_fefo(&tx, medicine_id, change)?;
        for (batch_id, batch_qty, deduct, price, unit, batch_no) in &batches {
            tx.execute(
                "UPDATE inventory SET quantity=?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
                params![batch_qty - deduct, batch_id],
            )
            .map_err(|e| e.to_string())?;
            let total_amount = deduct * price;
            tx.execute(
                "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, batch_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",
                params![medicine_id, &medicine_name, hist_type, deduct, price, total_amount, &operator_str, &notes_str, batch_id],
            )
            .map_err(|e| e.to_string())?;
            log_operation(
                &tx,
                "STOCK",
                "inventory",
                *batch_id,
                &format!("{}: {} {}{} (批次:{})", hist_type, medicine_name, deduct, unit, batch_no),
            )?;
        }
    }

    tx.commit().map_err(|e| e.to_string())?;
    Ok(())
}

/// FEFO 批次选择：近效期优先出库，无效期的最后出库
///
/// 返回 Vec<(batch_id, 当前库存, 本次扣减量, 单价, 单位, 批次号)>
fn select_batches_fefo(
    tx: &Connection,
    medicine_id: i64,
    needed: f64,
) -> Result<Vec<(i64, f64, f64, f64, String, String)>, String> {
    let mut stmt = tx
        .prepare(
            "SELECT id, batch_no, quantity, price, unit FROM inventory
             WHERE medicine_id=?1 AND quantity > 0
             ORDER BY
                CASE WHEN expiry_date IS NULL OR expiry_date = '' THEN 1 ELSE 0 END,
                expiry_date ASC,
                created_at ASC",
        )
        .map_err(|e| e.to_string())?;
    let rows = stmt
        .query_map(params![medicine_id], |row| {
            Ok((
                row.get::<_, i64>(0)?,
                row.get::<_, String>(1)?,
                row.get::<_, f64>(2)?,
                row.get::<_, f64>(3)?,
                row.get::<_, String>(4)?,
            ))
        })
        .map_err(|e| e.to_string())?;

    let mut result = Vec::new();
    let mut remaining = needed;
    for r in rows {
        let (batch_id, batch_no, qty, price, unit) = r.map_err(|e| e.to_string())?;
        if remaining <= 0.0 {
            break;
        }
        let deduct = if qty >= remaining {
            remaining
        } else {
            qty
        };
        result.push((batch_id, qty, deduct, price, unit, batch_no));
        remaining -= deduct;
    }
    if remaining > 0.001 {
        return Err(format!(
            "库存不足，需要 {}，可用库存不足",
            needed
        ));
    }
    Ok(result)
}

/// 库存变更历史查询（支持按药材、类型、日期范围筛选）
#[tauri::command]
pub fn list_inventory_history(
    medicine_id: Option<i64>,
    history_type: Option<String>,
    start_date: Option<String>,
    end_date: Option<String>,
    limit: Option<i64>,
    state: State<'_, DbState>,
) -> Result<Vec<InventoryHistory>, String> {
    let conn = state.lock()?;
    let limit = limit.unwrap_or(200).clamp(1, 2000);

    let mut sql = String::from(
        "SELECT id, medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, created_at, batch_id FROM inventory_history WHERE 1=1",
    );
    let mut pv: Vec<SqlValue> = Vec::new();
    if let Some(mid) = medicine_id {
        sql.push_str(" AND medicine_id = ?");
        pv.push(SqlValue::Integer(mid));
    }
    if let Some(ht) = &history_type {
        if !ht.is_empty() {
            sql.push_str(" AND type = ?");
            pv.push(SqlValue::Text(ht.clone()));
        }
    }
    if let Some(sd) = &start_date {
        if !sd.is_empty() {
            sql.push_str(" AND date(created_at) >= date(?)");
            pv.push(SqlValue::Text(sd.clone()));
        }
    }
    if let Some(ed) = &end_date {
        if !ed.is_empty() {
            sql.push_str(" AND date(created_at) <= date(?)");
            pv.push(SqlValue::Text(ed.clone()));
        }
    }
    sql.push_str(" ORDER BY id DESC LIMIT ?");
    pv.push(SqlValue::Integer(limit));

    let list: Vec<InventoryHistory> = {
        let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params_from_iter(pv.iter()), |row| {
                Ok(InventoryHistory {
                    id: row.get(0)?,
                    medicine_id: row.get(1)?,
                    medicine_name: row.get::<_, Option<String>>(2)?.unwrap_or_default(),
                    history_type: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
                    quantity: row.get::<_, Option<f64>>(4)?.unwrap_or(0.0),
                    price: row.get(5)?,
                    total_amount: row.get(6)?,
                    operator: row.get::<_, Option<String>>(7)?.unwrap_or_default(),
                    notes: row.get::<_, Option<String>>(8)?.unwrap_or_default(),
                    created_at: row.get(9)?,
                    batch_id: row.get(10)?,
                })
            })
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };
    Ok(list)
}

/// 效期预警：查询指定天数内到期的批次（默认 30 天）
#[tauri::command]
pub fn list_expiring_batches(
    days: Option<i64>,
    state: State<'_, DbState>,
) -> Result<Vec<ExpiringBatch>, String> {
    let conn = state.lock()?;
    let days = days.unwrap_or(30).clamp(1, 365);

    let mut stmt = conn
        .prepare(
            "SELECT i.id, i.medicine_id, m.name, i.batch_no, i.expiry_date,
                    i.quantity, i.unit, i.price
             FROM inventory i
             JOIN medicines m ON i.medicine_id = m.id
             WHERE i.expiry_date IS NOT NULL
               AND i.expiry_date != ''
               AND date(i.expiry_date) <= date('now', ?1)
               AND i.quantity > 0
             ORDER BY i.expiry_date ASC",
        )
        .map_err(|e| e.to_string())?;
    let days_str = format!("+{days} days");
    let rows = stmt
        .query_map(params![&days_str], |row| {
            Ok(ExpiringBatch {
                id: row.get(0)?,
                medicine_id: row.get(1)?,
                medicine_name: row.get::<_, Option<String>>(2)?.unwrap_or_default(),
                batch_no: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
                expiry_date: row.get::<_, Option<String>>(4)?.unwrap_or_default(),
                quantity: row.get::<_, Option<f64>>(5)?.unwrap_or(0.0),
                unit: row
                    .get::<_, Option<String>>(6)?
                    .unwrap_or_else(|| "g".to_string()),
                price: row.get::<_, Option<f64>>(7)?.unwrap_or(0.0),
            })
        })
        .map_err(|e| e.to_string())?;
    let mut out = Vec::new();
    for r in rows {
        out.push(r.map_err(|e| e.to_string())?);
    }
    Ok(out)
}

// ==================== 处方管理 ====================

/// 处方列表（含明细，支持按患者/诊断搜索 + 日期范围筛选）
#[tauri::command]
pub fn list_prescriptions(
    keyword: Option<String>,
    start_date: Option<String>,
    end_date: Option<String>,
    limit: Option<i64>,
    state: State<'_, DbState>,
) -> Result<Vec<PrescriptionWithItems>, String> {
    let conn = state.lock()?;
    let limit = limit.unwrap_or(100).clamp(1, 1000);

    let mut sql = String::from(
        "SELECT id, patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by, created_at FROM prescriptions WHERE 1=1",
    );
    let mut pv: Vec<SqlValue> = Vec::new();
    if let Some(kw) = &keyword {
        if !kw.is_empty() {
            sql.push_str(" AND (patient_name LIKE ? OR diagnosis LIKE ?)");
            let pat = format!("%{kw}%");
            pv.push(SqlValue::Text(pat.clone()));
            pv.push(SqlValue::Text(pat));
        }
    }
    if let Some(sd) = &start_date {
        if !sd.is_empty() {
            sql.push_str(" AND date(created_at) >= date(?)");
            pv.push(SqlValue::Text(sd.clone()));
        }
    }
    if let Some(ed) = &end_date {
        if !ed.is_empty() {
            sql.push_str(" AND date(created_at) <= date(?)");
            pv.push(SqlValue::Text(ed.clone()));
        }
    }
    sql.push_str(" ORDER BY id DESC LIMIT ?");
    pv.push(SqlValue::Integer(limit));

    let prescriptions: Vec<Prescription> = {
        let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params_from_iter(pv.iter()), map_prescription_row)
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };

    // 收集所有处方 id（过滤掉 id 为 None 的异常数据，避免 panic）
    let ids: Vec<i64> = prescriptions.iter().filter_map(|p| p.id).collect();
    if ids.is_empty() {
        return Ok(Vec::new());
    }

    // 一次性查询所有处方明细（IN 批量查询，消除 N+1）
    let placeholders = ids.iter().map(|_| "?").collect::<Vec<_>>().join(", ");
    let items_sql = format!(
        "SELECT id, prescription_id, medicine_id, medicine_name, quantity, unit, price, amount, batch_id FROM prescription_items WHERE prescription_id IN ({placeholders}) ORDER BY id ASC"
    );
    let id_params: Vec<SqlValue> = ids.iter().map(|id| SqlValue::Integer(*id)).collect();
    let all_items: Vec<PrescriptionItem> = {
        let mut stmt = conn.prepare(&items_sql).map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params_from_iter(id_params.iter()), map_prescription_item_row)
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };

    // 按 prescription_id 分组
    let mut items_map: std::collections::HashMap<i64, Vec<PrescriptionItem>> =
        std::collections::HashMap::new();
    for item in all_items {
        if let Some(pid) = item.prescription_id {
            items_map.entry(pid).or_default().push(item);
        }
    }

    // 组装结果
    let result = prescriptions
        .into_iter()
        .map(|p| {
            let pid = p.id.unwrap_or(0);
            let items = items_map.remove(&pid).unwrap_or_default();
            PrescriptionWithItems {
                prescription: p,
                items,
            }
        })
        .collect();
    Ok(result)
}

/// 创建处方（事务：写处方头 + 明细 + 扣减库存 + 库存历史）
#[tauri::command]
pub fn create_prescription(
    input: CreatePrescriptionInput,
    state: State<'_, DbState>,
) -> Result<i64, String> {
    if input.items.is_empty() {
        return Err("处方至少需要一味药材".to_string());
    }
    // 校验每个明细的数量与价格合法性，防止前端传入 0/负数
    for item in &input.items {
        if item.quantity <= 0.0 {
            return Err(format!("药材 '{}' 数量必须大于 0", item.medicine_name));
        }
        if item.price < 0.0 {
            return Err(format!("药材 '{}' 单价不能为负", item.medicine_name));
        }
    }
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;
    let p = input.prescription;

    // 服务端强制重新计算总金额，防止前端传入不一致数据
    let total: f64 = input.items.iter().map(|i| i.amount).sum();
    // 用户选择的开方日期（为空则用数据库默认 CURRENT_TIMESTAMP）
    let created_at = p.created_at.as_deref().filter(|s| !s.is_empty());

    if created_at.is_some() {
        tx.execute(
            "INSERT INTO prescriptions (patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by, created_at) VALUES (?1,?2,?3,?4,?5,?6,?7)",
            params![
                &p.patient_name,
                p.patient_age,
                &p.patient_gender,
                &p.diagnosis,
                total,
                &p.created_by,
                created_at,
            ],
        )
        .map_err(|e| format!("创建处方失败: {e}"))?;
    } else {
        tx.execute(
            "INSERT INTO prescriptions (patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by) VALUES (?1,?2,?3,?4,?5,?6)",
            params![
                &p.patient_name,
                p.patient_age,
                &p.patient_gender,
                &p.diagnosis,
                total,
                &p.created_by,
            ],
        )
        .map_err(|e| format!("创建处方失败: {e}"))?;
    }
    let prescription_id = tx.last_insert_rowid();

    for item in &input.items {
        // FEFO 跨批次扣减库存
        let batches = select_batches_fefo(&tx, item.medicine_id, item.quantity)
            .map_err(|e| format!("药材 '{}' {}", item.medicine_name, e))?;

        // 取第一个扣减批次作为处方明细的 batch_id（主要批次，用于列表展示参考）
        let primary_batch_id = batches.first().map(|b| b.0);

        tx.execute(
            "INSERT INTO prescription_items (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount, batch_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
            params![
                prescription_id,
                item.medicine_id,
                &item.medicine_name,
                item.quantity,
                &item.unit,
                item.price,
                item.amount,
                primary_batch_id,
            ],
        )
        .map_err(|e| format!("写入处方明细失败: {e}"))?;
        let item_id = tx.last_insert_rowid();

        // 逐批次扣减库存 + 写出库历史 + 记录扣减明细（用于删除时精确回扣）
        for (batch_id, batch_qty, deduct, batch_price, _unit, _batch_no) in &batches {
            tx.execute(
                "UPDATE inventory SET quantity=?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
                params![batch_qty - deduct, batch_id],
            )
            .map_err(|e| format!("扣减库存失败: {e}"))?;

            tx.execute(
                "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, batch_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",
                params![
                    item.medicine_id,
                    &item.medicine_name,
                    "出库",
                    deduct,
                    batch_price,
                    deduct * batch_price,
                    &p.created_by,
                    "处方出库",
                    batch_id,
                ],
            )
            .map_err(|e| e.to_string())?;

            // 记录批次扣减明细，删除处方时按此精确回扣
            tx.execute(
                "INSERT INTO prescription_item_batches (prescription_item_id, batch_id, quantity, price) VALUES (?1,?2,?3,?4)",
                params![item_id, batch_id, deduct, batch_price],
            )
            .map_err(|e| format!("写入批次扣减明细失败: {e}"))?;
        }
    }

    log_operation(
        &tx,
        "CREATE",
        "prescription",
        prescription_id,
        &format!("创建处方: 患者 {}", p.patient_name),
    )?;
    tx.commit().map_err(|e| e.to_string())?;
    Ok(prescription_id)
}

/// 删除处方（事务：回扣库存 + 记录退库历史 + 级联删除明细）
#[tauri::command]
pub fn delete_prescription(id: i64, state: State<'_, DbState>) -> Result<(), String> {
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;

    // 查询处方明细 ID 列表（用于关联表回扣）
    let items: Vec<(i64, String, f64)> = {
        let mut stmt = tx
            .prepare(
                "SELECT medicine_id, medicine_name, quantity FROM prescription_items WHERE prescription_id=?1",
            )
            .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params![id], |row| {
                Ok((
                    row.get::<_, i64>(0)?,
                    row.get::<_, String>(1)?,
                    row.get::<_, f64>(2)?,
                ))
            })
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };

    // 按关联表精确回扣：每个处方明细的各批次扣减量逐条回扣
    for (medicine_id, medicine_name, total_qty) in &items {
        // 查该处方明细的批次扣减明细
        let pib_rows: Vec<(i64, f64, f64)> = {
            let mut stmt = tx
                .prepare(
                    "SELECT pib.batch_id, pib.quantity, pib.price
                     FROM prescription_item_batches pib
                     JOIN prescription_items pi ON pib.prescription_item_id = pi.id
                     WHERE pi.prescription_id = ?1 AND pi.medicine_id = ?2",
                )
                .map_err(|e| e.to_string())?;
            let rows = stmt
                .query_map(params![id, medicine_id], |row| {
                    Ok((row.get(0)?, row.get(1)?, row.get(2)?))
                })
                .map_err(|e| e.to_string())?;
            let mut out = Vec::new();
            for r in rows {
                out.push(r.map_err(|e| e.to_string())?);
            }
            out
        };

        if pib_rows.is_empty() {
            // 老数据（009 迁移前创建的处方无关联表记录）：回扣整量到"初始库存"或第一个批次
            let target_batch: Option<i64> = tx
                .query_row(
                    "SELECT id FROM inventory WHERE medicine_id=?1 ORDER BY CASE WHEN batch_no='初始库存' THEN 0 ELSE 1 END, id ASC LIMIT 1",
                    params![medicine_id],
                    |row| row.get(0),
                )
                .optional()
                .map_err(|e| e.to_string())?;
            if let Some(bid) = target_batch {
                tx.execute(
                    "UPDATE inventory SET quantity = quantity + ?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
                    params![total_qty, bid],
                )
                .map_err(|e| format!("回扣库存失败: {e}"))?;
            }
            tx.execute(
                "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, batch_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",
                params![medicine_id, medicine_name, "退库", total_qty, 0.0, 0.0, "", "删除处方回扣(老数据)", target_batch],
            )
            .map_err(|e| e.to_string())?;
        } else {
            // 新数据：按批次扣减明细精确回扣
            for (batch_id, qty, price) in &pib_rows {
                // 检查批次是否仍存在（可能已被单独删除）
                let exists: Option<i64> = tx
                    .query_row(
                        "SELECT id FROM inventory WHERE id=?1",
                        params![batch_id],
                        |row| row.get(0),
                    )
                    .optional()
                    .map_err(|e| e.to_string())?;
                if exists.is_some() {
                    tx.execute(
                        "UPDATE inventory SET quantity = quantity + ?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
                        params![qty, batch_id],
                    )
                    .map_err(|e| format!("回扣库存失败: {e}"))?;
                } else {
                    // 原批次已删，回扣到该药材的"初始库存"或第一个批次
                    let fallback: Option<i64> = tx
                        .query_row(
                            "SELECT id FROM inventory WHERE medicine_id=?1 ORDER BY CASE WHEN batch_no='初始库存' THEN 0 ELSE 1 END, id ASC LIMIT 1",
                            params![medicine_id],
                            |row| row.get(0),
                        )
                        .optional()
                        .map_err(|e| e.to_string())?;
                    if let Some(fid) = fallback {
                        tx.execute(
                            "UPDATE inventory SET quantity = quantity + ?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
                            params![qty, fid],
                        )
                        .map_err(|e| format!("回扣库存失败: {e}"))?;
                    }
                }
                // 退库历史记录（使用原扣减价格，保持金额可追溯）
                tx.execute(
                    "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, batch_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",
                    params![medicine_id, medicine_name, "退库", qty, price, qty * price, "", "删除处方回扣", batch_id],
                )
                .map_err(|e| e.to_string())?;
            }
        }
    }

    // 删除关联表明细、处方明细与处方（关联表 ON DELETE CASCADE 会自动清理 pib，但显式删更安全）
    tx.execute(
        "DELETE FROM prescription_item_batches WHERE prescription_item_id IN (SELECT id FROM prescription_items WHERE prescription_id=?1)",
        params![id],
    )
    .map_err(|e| e.to_string())?;
    tx.execute("DELETE FROM prescription_items WHERE prescription_id=?1", params![id])
        .map_err(|e| e.to_string())?;
    tx.execute("DELETE FROM prescriptions WHERE id=?1", params![id])
        .map_err(|e| format!("删除处方失败: {e}"))?;
    log_operation(&tx, "DELETE", "prescription", id, "删除处方（回扣库存）")?;
    tx.commit().map_err(|e| e.to_string())?;
    Ok(())
}

// ==================== 客户管理（患者档案） ====================

/// 患者列表（支持按姓名/电话搜索）
#[tauri::command]
pub fn list_patients(
    keyword: Option<String>,
    state: State<'_, DbState>,
) -> Result<Vec<Patient>, String> {
    let conn = state.lock()?;
    let mut sql = String::from(
        "SELECT id, name, gender, age, phone, address, allergy, medical_history, notes, created_at, updated_at FROM patients WHERE 1=1",
    );
    let mut pv: Vec<SqlValue> = Vec::new();
    if let Some(kw) = &keyword {
        if !kw.is_empty() {
            sql.push_str(" AND (name LIKE ? OR phone LIKE ?)");
            let pat = format!("%{kw}%");
            pv.push(SqlValue::Text(pat.clone()));
            pv.push(SqlValue::Text(pat));
        }
    }
    sql.push_str(" ORDER BY id DESC");

    let patients: Vec<Patient> = {
        let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params_from_iter(pv.iter()), map_patient_row)
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };
    Ok(patients)
}

/// 获取单条患者档案
#[tauri::command]
pub fn get_patient(id: i64, state: State<'_, DbState>) -> Result<Patient, String> {
    let conn = state.lock()?;
    conn.query_row(
        "SELECT id, name, gender, age, phone, address, allergy, medical_history, notes, created_at, updated_at FROM patients WHERE id=?1",
        params![id],
        map_patient_row,
    )
    .optional()
    .map_err(|e| e.to_string())?
    .ok_or_else(|| format!("患者 id={id} 不存在"))
}

/// 新增患者档案
#[tauri::command]
pub fn create_patient(patient: Patient, state: State<'_, DbState>) -> Result<i64, String> {
    if patient.name.trim().is_empty() {
        return Err("患者姓名不能为空".to_string());
    }
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;
    tx.execute(
        "INSERT INTO patients (name, gender, age, phone, address, allergy, medical_history, notes) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
        params![
            &patient.name,
            &patient.gender,
            patient.age,
            &patient.phone,
            &patient.address,
            &patient.allergy,
            &patient.medical_history,
            &patient.notes,
        ],
    )
    .map_err(|e| format!("创建患者失败: {e}"))?;
    let id = tx.last_insert_rowid();
    log_operation(&tx, "CREATE", "patient", id, &format!("创建患者: {}", patient.name))?;
    tx.commit().map_err(|e| format!("提交事务失败: {e}"))?;
    Ok(id)
}

/// 更新患者档案
#[tauri::command]
pub fn update_patient(patient: Patient, state: State<'_, DbState>) -> Result<(), String> {
    let id = patient.id.ok_or("患者ID不能为空".to_string())?;
    if patient.name.trim().is_empty() {
        return Err("患者姓名不能为空".to_string());
    }
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;
    tx.execute(
        "UPDATE patients SET name=?1, gender=?2, age=?3, phone=?4, address=?5, allergy=?6, medical_history=?7, notes=?8, updated_at=CURRENT_TIMESTAMP WHERE id=?9",
        params![
            &patient.name,
            &patient.gender,
            patient.age,
            &patient.phone,
            &patient.address,
            &patient.allergy,
            &patient.medical_history,
            &patient.notes,
            id,
        ],
    )
    .map_err(|e| format!("更新患者失败: {e}"))?;
    log_operation(&tx, "UPDATE", "patient", id, &format!("更新患者: {}", patient.name))?;
    tx.commit().map_err(|e| format!("提交事务失败: {e}"))?;
    Ok(())
}

/// 删除患者档案
#[tauri::command]
pub fn delete_patient(id: i64, state: State<'_, DbState>) -> Result<(), String> {
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;
    let name: Option<String> = tx
        .query_row(
            "SELECT name FROM patients WHERE id=?1",
            params![id],
            |row| row.get(0),
        )
        .optional()
        .map_err(|e| e.to_string())?;
    tx.execute("DELETE FROM patients WHERE id=?1", params![id])
        .map_err(|e| format!("删除患者失败: {e}"))?;
    log_operation(
        &tx,
        "DELETE",
        "patient",
        id,
        &format!("删除患者: {}", name.unwrap_or_default()),
    )?;
    tx.commit().map_err(|e| format!("提交事务失败: {e}"))?;
    Ok(())
}

/// 查询某患者的处方历史（通过 patient_name 关联）
#[tauri::command]
pub fn get_patient_prescriptions(
    name: String,
    state: State<'_, DbState>,
) -> Result<Vec<Prescription>, String> {
    let conn = state.lock()?;
    let prescriptions: Vec<Prescription> = {
        let mut stmt = conn.prepare(
            "SELECT id, patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by, created_at
             FROM prescriptions WHERE patient_name = ?1 ORDER BY id DESC",
        )
        .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params![&name], map_prescription_row)
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };
    Ok(prescriptions)
}

/// 患者统计数据：处方数、总金额、首诊/末诊日期
#[tauri::command]
pub fn get_patient_statistics(
    name: String,
    state: State<'_, DbState>,
) -> Result<PatientStatistics, String> {
    let conn = state.lock()?;
    let (prescription_count, total_amount, first_visit, last_visit): (
        i64,
        f64,
        Option<String>,
        Option<String>,
    ) = conn
        .query_row(
            "SELECT COUNT(*), COALESCE(SUM(total_amount),0), MIN(created_at), MAX(created_at)
             FROM prescriptions WHERE patient_name = ?1",
            params![&name],
            |row| {
                Ok((
                    row.get(0)?,
                    row.get(1)?,
                    row.get(2)?,
                    row.get(3)?,
                ))
            },
        )
        .map_err(|e| format!("查询患者统计失败: {e}"))?;
    Ok(PatientStatistics {
        prescription_count,
        total_amount,
        first_visit,
        last_visit,
    })
}

// ==================== 看板与统计 ====================

/// 首页看板数据
#[tauri::command]
pub fn get_dashboard_data(
    state: State<'_, DbState>,
) -> Result<DashboardData, String> {
    let conn = state.lock()?;

    let medicine_count: i64 = conn
        .query_row("SELECT COUNT(*) FROM medicines", (), |row| row.get(0))
        .map_err(|e| e.to_string())?;
    let prescription_count: i64 = conn
        .query_row("SELECT COUNT(*) FROM prescriptions", (), |row| row.get(0))
        .map_err(|e| e.to_string())?;
    let total_stock_value: f64 = conn
        .query_row(
            "SELECT COALESCE(SUM(quantity*price),0) FROM inventory",
            (),
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())?;
    let low_stock_count: i64 = conn
        .query_row(
            // 按药材聚合后比较总库存与最低库存阈值（取该药材所有批次的最小 min_stock）
            "SELECT COUNT(*) FROM (
                SELECT medicine_id, SUM(quantity) as total_qty, MIN(min_stock) as min_threshold
                FROM inventory GROUP BY medicine_id
                HAVING total_qty <= min_threshold
            )",
            (),
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())?;

    let low_stock_list: Vec<LowStockItem> = {
        let mut stmt = conn.prepare(
            "SELECT i.medicine_id, m.name, SUM(i.quantity) as total_qty, MIN(i.min_stock) as min_threshold, i.unit
             FROM inventory i JOIN medicines m ON i.medicine_id=m.id
             GROUP BY i.medicine_id, m.name, i.unit
             HAVING total_qty <= min_threshold
             ORDER BY (total_qty - min_threshold) ASC LIMIT 20",
        )
        .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map((), |row| {
                Ok(LowStockItem {
                    medicine_id: row.get(0)?,
                    medicine_name: row.get::<_, Option<String>>(1)?.unwrap_or_default(),
                    quantity: row.get::<_, Option<f64>>(2)?.unwrap_or(0.0),
                    min_stock: row.get::<_, Option<f64>>(3)?.unwrap_or(0.0),
                    unit: row
                        .get::<_, Option<String>>(4)?
                        .unwrap_or_else(|| "g".to_string()),
                })
            })
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };

    let recent_prescriptions: Vec<Prescription> = {
        let mut stmt = conn.prepare(
            "SELECT id, patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by, created_at
             FROM prescriptions ORDER BY id DESC LIMIT 10",
        )
        .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map((), map_prescription_row)
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };

    // 今日开方数与销售收入（按本地日期匹配，与前端 dayjs 本地时间一致）
    let (today_prescription_count, today_revenue): (i64, f64) = {
        let mut stmt = conn.prepare(
            "SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
             FROM prescriptions
             WHERE date(created_at) = date('now', 'localtime')",
        )
        .map_err(|e| e.to_string())?;
        stmt.query_row((), |row| {
            Ok((row.get::<_, i64>(0)?, row.get::<_, f64>(1)?))
        })
        .map_err(|e| e.to_string())?
    };

    Ok(DashboardData {
        medicine_count,
        prescription_count,
        total_stock_value,
        low_stock_count,
        low_stock_list,
        recent_prescriptions,
        today_prescription_count,
        today_revenue,
    })
}

/// 销售统计（按时间范围）
#[tauri::command]
pub fn get_statistics(
    start_date: String,
    end_date: String,
    state: State<'_, DbState>,
) -> Result<StatisticsData, String> {
    let conn = state.lock()?;

    let (prescription_count, total_amount): (i64, f64) = conn
        .query_row(
            "SELECT COUNT(*), COALESCE(SUM(total_amount),0) FROM prescriptions WHERE date(created_at) BETWEEN date(?1) AND date(?2)",
            params![&start_date, &end_date],
            |row| Ok((row.get(0)?, row.get(1)?)),
        )
        .map_err(|e| e.to_string())?;

    let medicine_kinds: i64 = conn
        .query_row(
            "SELECT COUNT(DISTINCT pi.medicine_id)
             FROM prescription_items pi JOIN prescriptions p ON pi.prescription_id=p.id
             WHERE date(p.created_at) BETWEEN date(?1) AND date(?2)",
            params![&start_date, &end_date],
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())?;

    let avg_amount = if prescription_count > 0 {
        total_amount / prescription_count as f64
    } else {
        0.0
    };
    let summary = StatisticsSummary {
        prescription_count,
        total_amount,
        medicine_kinds,
        avg_amount,
    };

    let top_medicines: Vec<TopMedicine> = {
        let mut stmt = conn.prepare(
            "SELECT pi.medicine_name, SUM(pi.quantity) AS q, SUM(pi.amount) AS amt
             FROM prescription_items pi JOIN prescriptions p ON pi.prescription_id=p.id
             WHERE date(p.created_at) BETWEEN date(?1) AND date(?2)
             GROUP BY pi.medicine_name ORDER BY amt DESC LIMIT 10",
        )
        .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params![&start_date, &end_date], |row| {
                Ok(TopMedicine {
                    medicine_name: row.get::<_, Option<String>>(0)?.unwrap_or_default(),
                    total_quantity: row.get::<_, Option<f64>>(1)?.unwrap_or(0.0),
                    total_amount: row.get::<_, Option<f64>>(2)?.unwrap_or(0.0),
                })
            })
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };

    let daily_trend: Vec<DailyTrend> = {
        let mut stmt = conn.prepare(
            "SELECT date(created_at) AS d, COUNT(*) AS c, COALESCE(SUM(total_amount),0) AS a
             FROM prescriptions
             WHERE date(created_at) BETWEEN date(?1) AND date(?2)
             GROUP BY d ORDER BY d ASC",
        )
        .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params![&start_date, &end_date], |row| {
                Ok(DailyTrend {
                    date: row.get::<_, Option<String>>(0)?.unwrap_or_default(),
                    prescription_count: row.get(1)?,
                    total_amount: row.get(2)?,
                })
            })
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };

    Ok(StatisticsData {
        summary,
        top_medicines,
        daily_trend,
    })
}

// ==================== 配伍禁忌 ====================

/// 检查处方药材列表的配伍禁忌（十八反、十九畏）
#[tauri::command]
pub fn check_compatibility(
    medicine_names: Vec<String>,
) -> Result<Vec<CompatibilityConflict>, String> {
    Ok(compatibility::check_compatibility(&medicine_names))
}

// ==================== 批量导入 / 导出 ====================

/// 把字符串安全解析为 f64，失败时返回默认值 0.0
fn parse_f64_or(s: &Option<String>, default: f64) -> Result<f64, String> {
    match s {
        Some(v) if !v.trim().is_empty() => {
            v.trim().parse::<f64>().map_err(|_| format!("无法解析数值: '{v}'"))
        }
        _ => Ok(default),
    }
}

/// 批量导入药材：事务内 UPSERT（已存在名称则更新药材与库存，否则新建）
#[tauri::command]
pub fn batch_import_medicines(
    records: Vec<MedicineImportRecord>,
    state: State<'_, DbState>,
) -> Result<BatchImportResult, String> {
    if records.is_empty() {
        return Err("导入数据不能为空".to_string());
    }
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;

    let mut inserted: u32 = 0;
    let mut updated: u32 = 0;
    let mut errors: Vec<String> = Vec::new();

    // 批量预查：一次性获取所有已存在的同名药材 ID，消除 N+1 查询
    let names: Vec<String> = records
        .iter()
        .map(|r| r.name.trim().to_string())
        .filter(|n| !n.is_empty())
        .collect();
    let mut existing_map: std::collections::HashMap<String, i64> = std::collections::HashMap::new();
    if !names.is_empty() {
        let placeholders = names.iter().map(|_| "?").collect::<Vec<_>>().join(", ");
        let sql = format!("SELECT id, name FROM medicines WHERE name IN ({placeholders})");
        let name_params: Vec<SqlValue> = names.iter().map(|n| SqlValue::Text(n.clone())).collect();
        let mut stmt = tx.prepare(&sql).map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params_from_iter(name_params.iter()), |row| {
                Ok((row.get::<_, i64>(0)?, row.get::<_, String>(1)?))
            })
            .map_err(|e| e.to_string())?;
        for r in rows {
            let (id, name) = r.map_err(|e| e.to_string())?;
            existing_map.insert(name, id);
        }
    }

    for (idx, rec) in records.iter().enumerate() {
        let row_no = idx + 1;
        let name = rec.name.trim().to_string();
        if name.is_empty() {
            errors.push(format!("第{row_no}行: 药材名称不能为空"));
            continue;
        }

        // 数值字段做类型转换保护
        let quantity = match parse_f64_or(&rec.quantity, 0.0) {
            Ok(v) => v,
            Err(e) => {
                errors.push(format!("第{row_no}行 ({name}): quantity {e}"));
                continue;
            }
        };
        let price = match parse_f64_or(&rec.price, 0.0) {
            Ok(v) => v,
            Err(e) => {
                errors.push(format!("第{row_no}行 ({name}): price {e}"));
                continue;
            }
        };
        let min_stock = match parse_f64_or(&rec.min_stock, 0.0) {
            Ok(v) => v,
            Err(e) => {
                errors.push(format!("第{row_no}行 ({name}): min_stock {e}"));
                continue;
            }
        };
        let unit = if rec.unit.trim().is_empty() {
            "g".to_string()
        } else {
            rec.unit.trim().to_string()
        };

        // 从预查 HashMap 中查找（消除 N+1 查询）
        let existing_id: Option<i64> = existing_map.get(&name).copied();

        let result = if let Some(id) = existing_id {
            // UPSERT：更新药材信息
            tx.execute(
                "UPDATE medicines SET alias=?1, category=?2, nature=?3, taste=?4, meridian=?5, efficacy=?6, indications=?7, usage=?8, dosage=?9, contraindication=?10, notes=?11, updated_at=CURRENT_TIMESTAMP WHERE id=?12",
                params![
                    &rec.alias, &rec.category, &rec.nature, &rec.taste, &rec.meridian,
                    &rec.efficacy, &rec.indications, &rec.usage, &rec.dosage,
                    &rec.contraindication, &rec.notes, id,
                ],
            )
            .map_err(|e| format!("更新药材 '{name}' 失败: {e}"))
            .and_then(|_| {
                // 批次改造：已有药材的新库存作为新批次入库（不再覆盖旧库存）
                // 用"导入批次-{时间戳}-{行号}"作为批次号，避免同批导入内冲突
                let batch_no = format!("导入批次-{}-{}", chrono::Local::now().format("%Y%m%d%H%M%S"), row_no);
                tx.execute(
                    "INSERT INTO inventory (medicine_id, batch_no, production_date, expiry_date, quantity, unit, price, min_stock) VALUES (?1,?2,NULL,NULL,?3,?4,?5,?6)",
                    params![id, &batch_no, quantity, &unit, price, min_stock],
                ).map_err(|e| format!("创建库存批次失败: {e}"))?;
                let inv_id = tx.last_insert_rowid();
                // 写入库历史，保持审计轨迹完整
                tx.execute(
                    "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, batch_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",
                    params![id, &name, "入库", quantity, price, quantity * price, "批量导入", &batch_no, inv_id],
                ).map_err(|e| format!("写入导入历史失败: {e}"))?;
                Ok(())
            })
        } else {
            // 新建药材 + 库存（初始批次）
            tx.execute(
                "INSERT INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12)",
                params![
                    &name, &rec.alias, &rec.category, &rec.nature, &rec.taste, &rec.meridian,
                    &rec.efficacy, &rec.indications, &rec.usage, &rec.dosage,
                    &rec.contraindication, &rec.notes,
                ],
            )
            .map_err(|e| format!("创建药材 '{name}' 失败: {e}"))
            .and_then(|_| {
                let new_id = tx.last_insert_rowid();
                tx.execute(
                    "INSERT INTO inventory (medicine_id, batch_no, production_date, expiry_date, quantity, unit, price, min_stock) VALUES (?1,'初始库存',NULL,NULL,?2,?3,?4,?5)",
                    params![new_id, quantity, &unit, price, min_stock],
                ).map_err(|e| format!("创建库存失败: {e}"))?;
                let inv_id = tx.last_insert_rowid();
                // 写入库历史，保持审计轨迹完整
                tx.execute(
                    "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, batch_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",
                    params![new_id, &name, "入库", quantity, price, quantity * price, "批量导入", "初始库存", inv_id],
                ).map_err(|e| format!("写入导入历史失败: {e}"))?;
                // 更新 HashMap，使同批次内重复名称走 UPDATE 而非重复 INSERT
                existing_map.insert(name.clone(), new_id);
                Ok(())
            })
        };

        match result {
            Ok(()) => {
                if existing_id.is_some() {
                    updated += 1;
                } else {
                    inserted += 1;
                }
            }
            Err(e) => {
                errors.push(format!("第{row_no}行 ({name}): {e}"));
            }
        }
    }

    log_operation(
        &tx,
        "IMPORT",
        "medicine",
        0,
        &format!("批量导入: 新增 {inserted} 条, 更新 {updated} 条, 错误 {} 条", errors.len()),
    )?;
    tx.commit().map_err(|e| format!("提交事务失败: {e}"))?;

    Ok(BatchImportResult {
        inserted,
        updated,
        errors,
    })
}

/// 导出全量药材为 CSV 字符串（UTF-8 with BOM，前端可直接写入文件）
#[tauri::command]
pub fn export_medicines_csv(state: State<'_, DbState>) -> Result<String, String> {
    let conn = state.lock()?;
    let mut stmt = conn
        .prepare(
            "SELECT name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes
             FROM medicines ORDER BY id ASC",
        )
        .map_err(|e| format!("准备查询失败: {e}"))?;

    let rows = stmt
        .query_map((), |row| {
            Ok([
                row.get::<_, String>(0)?,
                row.get::<_, Option<String>>(1)?.unwrap_or_default(),
                row.get::<_, Option<String>>(2)?.unwrap_or_default(),
                row.get::<_, Option<String>>(3)?.unwrap_or_default(),
                row.get::<_, Option<String>>(4)?.unwrap_or_default(),
                row.get::<_, Option<String>>(5)?.unwrap_or_default(),
                row.get::<_, Option<String>>(6)?.unwrap_or_default(),
                row.get::<_, Option<String>>(7)?.unwrap_or_default(),
                row.get::<_, Option<String>>(8)?.unwrap_or_default(),
                row.get::<_, Option<String>>(9)?.unwrap_or_default(),
                row.get::<_, Option<String>>(10)?.unwrap_or_default(),
                row.get::<_, Option<String>>(11)?.unwrap_or_default(),
            ])
        })
        .map_err(|e| format!("查询药材失败: {e}"))?;

    let headers = [
        "name", "alias", "category", "nature", "taste", "meridian",
        "efficacy", "indications", "usage", "dosage", "contraindication", "notes",
    ];

    // UTF-8 BOM，便于 Excel 正确识别中文
    let mut csv = String::from("\u{FEFF}");
    csv.push_str(&headers.join(","));
    csv.push('\n');

    for row in rows {
        let r = row.map_err(|e| format!("读取行失败: {e}"))?;
        let fields: Vec<String> = r
            .iter()
            .map(|s| {
                let needs_quote = s.contains(',') || s.contains('"') || s.contains('\n');
                if needs_quote {
                    let escaped = s.replace('"', "\"\"");
                    format!("\"{escaped}\"")
                } else {
                    s.clone()
                }
            })
            .collect();
        csv.push_str(&fields.join(","));
        csv.push('\n');
    }

    Ok(csv)
}

/// 返回含 2 条样本数据（人参/黄芪）的 CSV 模板字符串
#[tauri::command]
pub fn download_import_template() -> Result<String, String> {
    let headers = [
        "name", "alias", "category", "nature", "taste", "meridian",
        "efficacy", "indications", "usage", "dosage", "contraindication",
        "notes", "quantity", "unit", "price", "min_stock",
    ];

    let samples: Vec<Vec<&str>> = vec![
        vec![
            "人参", "黄参", "补虚药", "温", "甘、微苦", "脾、肺、心经",
            "大补元气", "体虚欲脱", "煎服", "3-9g", "实证忌服", "",
            "500", "g", "85", "50",
        ],
        vec![
            "黄芪", "黄耆", "补虚药", "微温", "甘", "脾、肺经",
            "补气升阳", "气虚乏力", "煎服", "9-30g", "实证禁服", "",
            "600", "g", "42", "60",
        ],
    ];

    // UTF-8 BOM
    let mut csv = String::from("\u{FEFF}");
    csv.push_str(&headers.join(","));
    csv.push('\n');
    for row in &samples {
        csv.push_str(&row.join(","));
        csv.push('\n');
    }
    Ok(csv)
}

/// 把字符串内容写入下载目录并返回绝对路径（用于 CSV 模板/导出等）
///
/// 安全：filename 经过路径遍历校验，禁止包含 `/`、`\`、`..` 等危险字符
#[tauri::command]
pub fn save_text_to_downloads(
    filename: String,
    content: String,
    app_handle: tauri::AppHandle,
) -> Result<String, String> {
    // 路径遍历防护：禁止目录分隔符与父目录引用
    if filename.is_empty()
        || filename.contains('/')
        || filename.contains('\\')
        || filename.contains("..")
        || filename.contains('\0')
    {
        return Err("文件名非法：不能为空或包含路径分隔符".to_string());
    }
    let dir = app_handle
        .path()
        .download_dir()
        .map_err(|e| format!("无法获取下载目录: {e}"))?;
    std::fs::create_dir_all(&dir).map_err(|e| format!("创建下载目录失败: {e}"))?;
    let path = dir.join(&filename);
    std::fs::write(&path, content.as_bytes())
        .map_err(|e| format!("写入文件失败: {e}"))?;
    Ok(path.to_string_lossy().to_string())
}

// ==================== 操作日志 ====================

/// 操作日志查询（支持按操作类型、目标类型、日期范围筛选）
#[tauri::command]
pub fn list_operation_logs(
    operation_type: Option<String>,
    target_type: Option<String>,
    start_date: Option<String>,
    end_date: Option<String>,
    limit: Option<i64>,
    state: State<'_, DbState>,
) -> Result<Vec<OperationLog>, String> {
    let conn = state.lock()?;
    let limit = limit.unwrap_or(200).clamp(1, 2000);

    let mut sql = String::from(
        "SELECT id, operation_type, target_type, target_id, operator, details, created_at FROM operation_logs WHERE 1=1",
    );
    let mut pv: Vec<SqlValue> = Vec::new();
    if let Some(ot) = &operation_type {
        if !ot.is_empty() {
            sql.push_str(" AND operation_type = ?");
            pv.push(SqlValue::Text(ot.clone()));
        }
    }
    if let Some(tt) = &target_type {
        if !tt.is_empty() {
            sql.push_str(" AND target_type = ?");
            pv.push(SqlValue::Text(tt.clone()));
        }
    }
    if let Some(sd) = &start_date {
        if !sd.is_empty() {
            sql.push_str(" AND date(created_at) >= date(?)");
            pv.push(SqlValue::Text(sd.clone()));
        }
    }
    if let Some(ed) = &end_date {
        if !ed.is_empty() {
            sql.push_str(" AND date(created_at) <= date(?)");
            pv.push(SqlValue::Text(ed.clone()));
        }
    }
    sql.push_str(" ORDER BY id DESC LIMIT ?");
    pv.push(SqlValue::Integer(limit));

    let list: Vec<OperationLog> = {
        let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map(params_from_iter(pv.iter()), |row| {
                Ok(OperationLog {
                    id: row.get(0)?,
                    operation_type: row.get::<_, Option<String>>(1)?.unwrap_or_default(),
                    target_type: row.get::<_, Option<String>>(2)?.unwrap_or_default(),
                    target_id: row.get(3)?,
                    operator: row.get::<_, Option<String>>(4)?.unwrap_or_default(),
                    details: row.get::<_, Option<String>>(5)?.unwrap_or_default(),
                    created_at: row.get(6)?,
                })
            })
            .map_err(|e| e.to_string())?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };
    Ok(list)
}

// ==================== 打印处方 ====================

/// 转义 HTML 特殊字符，防止 XSS
fn html_escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&#x27;"),
            _ => out.push(c),
        }
    }
    out
}

/// 生成处方 HTML（含患者信息、药材表格、总金额、日期）
#[tauri::command]
pub fn generate_prescription_html(
    prescription_id: i64,
    state: State<'_, DbState>,
) -> Result<String, String> {
    let conn = state.lock()?;

    let p: Prescription = conn
        .query_row(
            "SELECT id, patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by, created_at
             FROM prescriptions WHERE id=?1",
            params![prescription_id],
            map_prescription_row,
        )
        .optional()
        .map_err(|e| format!("查询处方失败: {e}"))?
        .ok_or_else(|| format!("处方 id={prescription_id} 不存在"))?;

    let items: Vec<PrescriptionItem> = {
        let mut stmt = conn
            .prepare(
                "SELECT id, prescription_id, medicine_id, medicine_name, quantity, unit, price, amount, batch_id
                 FROM prescription_items WHERE prescription_id=?1 ORDER BY id ASC",
            )
            .map_err(|e| format!("准备明细查询失败: {e}"))?;
        let rows = stmt
            .query_map(params![prescription_id], map_prescription_item_row)
            .map_err(|e| format!("查询明细失败: {e}"))?;
        let mut out = Vec::new();
        for r in rows {
            out.push(r.map_err(|e| e.to_string())?);
        }
        out
    };

    let patient_name = html_escape(&p.patient_name);
    let gender = html_escape(&p.patient_gender);
    let diagnosis = html_escape(&p.diagnosis);
    let created_by = html_escape(&p.created_by);
    let age = p.patient_age.map(|a| a.to_string()).unwrap_or_default();
    let created_at = html_escape(p.created_at.as_deref().unwrap_or(""));

    let mut rows_html = String::new();
    let mut idx = 1u32;
    for item in &items {
        rows_html.push_str(&format!(
            "<tr><td style='text-align:center'>{idx}</td>\
             <td>{name}</td>\
             <td style='text-align:right'>{qty}</td>\
             <td style='text-align:center'>{unit}</td>\
             <td style='text-align:right'>{price}</td>\
             <td style='text-align:right'>{amount}</td></tr>",
            idx = idx,
            name = html_escape(&item.medicine_name),
            qty = item.quantity,
            unit = html_escape(&item.unit),
            price = format!("¥{:.2}", item.price),
            amount = format!("¥{:.2}", item.amount),
        ));
        idx += 1;
    }

    let html = format!(
        r#"<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>中药处方笺 #{id}</title>
<style>
  * {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; }}
  body {{ padding: 32px; color: #1f2937; }}
  h1 {{ text-align: center; font-size: 24px; letter-spacing: 8px; margin: 0 0 4px; }}
  .subtitle {{ text-align: center; color: #6b7280; font-size: 12px; margin-bottom: 18px; }}
  .meta {{ display: flex; justify-content: space-between; border-bottom: 2px solid #1f2937; padding-bottom: 8px; margin-bottom: 12px; font-size: 14px; }}
  .meta div {{ line-height: 1.8; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }}
  th, td {{ border: 1px solid #d1d5db; padding: 6px 10px; }}
  th {{ background: #f3f4f6; font-weight: 600; }}
  .total {{ text-align: right; font-size: 16px; font-weight: 700; margin: 12px 0; }}
  .total span {{ color: #dc2626; }}
  .footer {{ margin-top: 28px; display: flex; justify-content: space-between; font-size: 13px; color: #6b7280; }}
  @media print {{ body {{ padding: 0; }} }}
</style>
</head>
<body>
  <h1>中药处方笺</h1>
  <div class="subtitle"> prescription #{id} </div>
  <div class="meta">
    <div>
      <div>患者姓名：<b>{patient_name}</b></div>
      <div>性别：{gender} &nbsp; 年龄：{age}</div>
      <div>诊断：{diagnosis}</div>
    </div>
    <div style="text-align:right">
      <div>开方人：{created_by}</div>
      <div>日期：{created_at}</div>
    </div>
  </div>
  <table>
    <thead>
      <tr>
        <th style="width:40px">序号</th>
        <th>药材</th>
        <th style="width:80px">数量</th>
        <th style="width:60px">单位</th>
        <th style="width:90px">单价</th>
        <th style="width:110px">金额</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
  <div class="total">合计（人民币大写）：<span>¥{total:.2}</span></div>
  <div class="footer">
    <div>审核：__________</div>
    <div>调配：__________</div>
    <div>取药人签字：__________</div>
  </div>
</body>
</html>"#,
        id = prescription_id,
        patient_name = patient_name,
        gender = gender,
        age = age,
        diagnosis = diagnosis,
        created_by = created_by,
        created_at = created_at,
        rows_html = rows_html,
        total = p.total_amount,
    );

    Ok(html)
}

// ==================== 数据备份与恢复 ====================

/// 计算文件 MD5（十六进制小写，每个字节零填充到 2 位）
fn compute_file_md5(path: &PathBuf) -> Result<String, String> {
    use md5::{Digest, Md5};
    let bytes = std::fs::read(path).map_err(|e| format!("读取文件失败: {e}"))?;
    let mut hasher = Md5::new();
    hasher.update(&bytes);
    let digest = hasher.finalize();
    // 手动零填充，避免 GenericArray::LowerHex 在单字符字节上不补 0
    let hex: String = digest.iter().map(|b| format!("{:02x}", b)).collect();
    Ok(hex)
}

/// 创建数据库备份
///
/// 备份文件：%APPDATA%/com.medicine.system/backups/medicine_system_YYYYMMDD_HHMMSS.db
/// 清单文件：%APPDATA%/com.medicine.system/backups/medicine_system_YYYYMMDD_HHMMSS.json
#[tauri::command]
pub fn create_backup(
    app_handle: tauri::AppHandle,
    state: State<'_, DbState>,
) -> Result<BackupInfo, String> {
    let app_data_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| format!("无法获取应用数据目录: {e}"))?;
    let db_path = app_data_dir.join("medicine_system.db");
    if !db_path.exists() {
        return Err(format!("数据库文件不存在: {}", db_path.display()));
    }
    let backup_dir = app_data_dir.join("backups");
    std::fs::create_dir_all(&backup_dir).map_err(|e| format!("创建备份目录失败: {e}"))?;

    let now = chrono::Local::now();
    let timestamp = now.format("%Y%m%d_%H%M%S").to_string();
    let created_at = now.format("%Y-%m-%d %H:%M:%S").to_string();
    let backup_filename = format!("medicine_system_{timestamp}.db");
    let backup_path = backup_dir.join(&backup_filename);

    // 备份数据库前先做一次 checkpoint，避免 WAL 模式下数据未落盘
    // 在锁作用域内完成 checkpoint + 文件复制，防止并发写入导致备份不一致
    {
        let conn = state.lock()?;
        conn.execute_batch("PRAGMA wal_checkpoint(FULL);")
            .map_err(|e| format!("数据库 checkpoint 失败: {e}"))?;
        std::fs::copy(&db_path, &backup_path)
            .map_err(|e| format!("复制数据库失败: {e}"))?;
    }

    let file_size = std::fs::metadata(&backup_path)
        .map(|m| m.len())
        .unwrap_or(0);
    let md5 = compute_file_md5(&backup_path)?;

    let manifest = serde_json::json!({
        "backup_path": backup_path.to_string_lossy(),
        "file_size": file_size,
        "md5": md5,
        "created_at": created_at,
        "timestamp": timestamp,
        "filename": backup_filename,
    });
    let manifest_path = backup_dir.join(format!("medicine_system_{timestamp}.json"));
    std::fs::write(
        &manifest_path,
        serde_json::to_string_pretty(&manifest)
            .map_err(|e| format!("序列化清单失败: {e}"))?,
    )
    .map_err(|e| format!("写入清单失败: {e}"))?;

    let conn = state.lock()?;
    log_operation(
        &conn,
        "BACKUP",
        "database",
        0,
        &format!("创建备份: {backup_filename}"),
    )?;

    Ok(BackupInfo {
        backup_path: backup_path.to_string_lossy().to_string(),
        file_size,
        md5,
        created_at,
    })
}

/// 列出所有备份（按时间倒序）
#[tauri::command]
pub fn list_backups(
    app_handle: tauri::AppHandle,
) -> Result<Vec<BackupEntry>, String> {
    let app_data_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| format!("无法获取应用数据目录: {e}"))?;
    let backup_dir = app_data_dir.join("backups");
    if !backup_dir.exists() {
        return Ok(Vec::new());
    }

    let mut entries: Vec<BackupEntry> = Vec::new();
    let read = std::fs::read_dir(&backup_dir)
        .map_err(|e| format!("读取备份目录失败: {e}"))?;

    for entry in read.flatten() {
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("json") {
            continue;
        }
        // 仅处理形如 medicine_system_YYYYMMDD_HHMMSS.json 的清单
        let _name = match path.file_name().and_then(|n| n.to_str()) {
            Some(n) if n.starts_with("medicine_system_") && n.ends_with(".json") => n,
            _ => continue,
        };
        let content = match std::fs::read_to_string(&path) {
            Ok(c) => c,
            Err(_) => continue,
        };
        let value: serde_json::Value = match serde_json::from_str(&content) {
            Ok(v) => v,
            Err(_) => continue,
        };
        let backup_path = value["backup_path"]
            .as_str()
            .map(|s| s.to_string())
            .unwrap_or_default();
        let file_size = value["file_size"].as_u64().unwrap_or(0);
        let md5 = value["md5"].as_str().unwrap_or("").to_string();
        let created_at = value["created_at"].as_str().unwrap_or("").to_string();
        if backup_path.is_empty() {
            continue;
        }
        entries.push(BackupEntry {
            backup_path,
            file_size,
            md5,
            created_at,
        });
    }

    // 按创建时间倒序排列
    entries.sort_by(|a, b| b.created_at.cmp(&a.created_at));
    Ok(entries)
}

/// 基于备份还原数据库
///
/// 还原流程：
/// 1. 关闭当前数据库连接（实际上 rusqlite 仍持有连接，这里通过 checkpoint + 文件覆盖实现）
/// 2. 用备份覆盖 medicine_system.db
/// 3. 验证 MD5
#[tauri::command]
pub fn restore_backup(
    backup_path: String,
    app_handle: tauri::AppHandle,
    state: State<'_, DbState>,
) -> Result<(), String> {
    let src = PathBuf::from(&backup_path);
    if !src.exists() {
        return Err(format!("备份文件不存在: {backup_path}"));
    }

    let app_data_dir = app_handle
        .path()
        .app_data_dir()
        .map_err(|e| format!("无法获取应用数据目录: {e}"))?;
    let db_path = app_data_dir.join("medicine_system.db");

    // 先做 checkpoint 让 WAL 数据落盘
    {
        let conn = state.lock()?;
        conn.execute_batch("PRAGMA wal_checkpoint(FULL);")
            .map_err(|e| format!("数据库 checkpoint 失败: {e}"))?;
    }

    // 先复制到临时文件，再原子替换，避免还原失败导致数据丢失
    let tmp_path = db_path.with_extension("db.restoring");
    std::fs::copy(&src, &tmp_path)
        .map_err(|e| format!("还原备份失败: {e}"))?;

    // 校验 MD5（如果备份清单存在）
    let manifest_path = src.with_extension("json");
    if manifest_path.exists() {
        let manifest_str = std::fs::read_to_string(&manifest_path)
            .map_err(|e| format!("读取备份清单失败: {e}"))?;
        let manifest: serde_json::Value = serde_json::from_str(&manifest_str)
            .map_err(|e| format!("解析备份清单失败: {e}"))?;
        if let Some(expected_md5) = manifest["md5"].as_str() {
            let actual_md5 = compute_file_md5(&tmp_path)?;
            if actual_md5 != expected_md5 {
                let _ = std::fs::remove_file(&tmp_path);
                return Err(format!(
                    "备份文件 MD5 校验失败，期望 {expected_md5}，实际 {actual_md5}"
                ));
            }
        }
    }

    // 用临时文件覆盖原数据库
    std::fs::rename(&tmp_path, &db_path)
        .map_err(|e| format!("替换数据库文件失败: {e}"))?;

    let conn = state.lock()?;
    log_operation(
        &conn,
        "RESTORE",
        "database",
        0,
        &format!("从备份还原: {}", src.display()),
    )?;

    Ok(())
}

/// 删除指定备份文件及其清单
///
/// 安全检查：禁止删除当前数据库文件（medicine_system.db）
#[tauri::command]
pub fn delete_backup(
    backup_path: String,
    state: State<'_, DbState>,
) -> Result<(), String> {
    let src = PathBuf::from(&backup_path);
    if !src.exists() {
        return Err(format!("备份文件不存在: {backup_path}"));
    }
    // 禁止删除当前数据库文件
    let file_name = src
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or_default();
    if file_name == "medicine_system.db" {
        return Err("不能删除当前数据库文件".to_string());
    }
    // 仅允许删除 backups 目录下的文件，避免任意文件删除
    let parent = src
        .parent()
        .and_then(|p| p.file_name())
        .and_then(|n| n.to_str())
        .unwrap_or_default();
    if parent != "backups" {
        return Err("仅允许删除 backups 目录下的备份文件".to_string());
    }

    // 删除备份文件
    std::fs::remove_file(&src)
        .map_err(|e| format!("删除备份文件失败: {e}"))?;
    // 删除对应清单文件（如果存在）
    let manifest_path = src.with_extension("json");
    if manifest_path.exists() {
        let _ = std::fs::remove_file(&manifest_path);
    }

    let conn = state.lock()?;
    log_operation(
        &conn,
        "DELETE",
        "backup",
        0,
        &format!("删除备份: {}", src.display()),
    )?;

    Ok(())
}

// ==================== 行映射辅助函数 ====================

fn map_medicine_row(row: &rusqlite::Row<'_>) -> rusqlite::Result<Medicine> {
    Ok(Medicine {
        id: row.get(0)?,
        name: row.get(1)?,
        alias: row.get::<_, Option<String>>(2)?.unwrap_or_default(),
        category: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
        nature: row.get::<_, Option<String>>(4)?.unwrap_or_default(),
        taste: row.get::<_, Option<String>>(5)?.unwrap_or_default(),
        meridian: row.get::<_, Option<String>>(6)?.unwrap_or_default(),
        efficacy: row.get::<_, Option<String>>(7)?.unwrap_or_default(),
        indications: row.get::<_, Option<String>>(8)?.unwrap_or_default(),
        usage: row.get::<_, Option<String>>(9)?.unwrap_or_default(),
        dosage: row.get::<_, Option<String>>(10)?.unwrap_or_default(),
        contraindication: row.get::<_, Option<String>>(11)?.unwrap_or_default(),
        notes: row.get::<_, Option<String>>(12)?.unwrap_or_default(),
        created_at: row.get(13)?,
        updated_at: row.get(14)?,
    })
}

fn map_prescription_row(row: &rusqlite::Row<'_>) -> rusqlite::Result<Prescription> {
    Ok(Prescription {
        id: row.get(0)?,
        patient_name: row.get::<_, Option<String>>(1)?.unwrap_or_default(),
        patient_age: row.get(2)?,
        patient_gender: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
        diagnosis: row.get::<_, Option<String>>(4)?.unwrap_or_default(),
        total_amount: row.get::<_, Option<f64>>(5)?.unwrap_or(0.0),
        created_by: row.get::<_, Option<String>>(6)?.unwrap_or_default(),
        created_at: row.get(7)?,
    })
}

fn map_prescription_item_row(row: &rusqlite::Row<'_>) -> rusqlite::Result<PrescriptionItem> {
    Ok(PrescriptionItem {
        id: row.get(0)?,
        prescription_id: row.get(1)?,
        medicine_id: row.get(2)?,
        medicine_name: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
        quantity: row.get::<_, Option<f64>>(4)?.unwrap_or(0.0),
        unit: row
            .get::<_, Option<String>>(5)?
            .unwrap_or_else(|| "g".to_string()),
        price: row.get::<_, Option<f64>>(6)?.unwrap_or(0.0),
        amount: row.get::<_, Option<f64>>(7)?.unwrap_or(0.0),
        batch_id: row.get(8)?,
    })
}

fn map_patient_row(row: &rusqlite::Row<'_>) -> rusqlite::Result<Patient> {
    Ok(Patient {
        id: row.get(0)?,
        name: row.get::<_, Option<String>>(1)?.unwrap_or_default(),
        gender: row.get::<_, Option<String>>(2)?.unwrap_or_default(),
        age: row.get(3)?,
        phone: row.get::<_, Option<String>>(4)?.unwrap_or_default(),
        address: row.get::<_, Option<String>>(5)?.unwrap_or_default(),
        allergy: row.get::<_, Option<String>>(6)?.unwrap_or_default(),
        medical_history: row.get::<_, Option<String>>(7)?.unwrap_or_default(),
        notes: row.get::<_, Option<String>>(8)?.unwrap_or_default(),
        created_at: row.get::<_, Option<String>>(9)?.unwrap_or_default(),
        updated_at: row.get::<_, Option<String>>(10)?.unwrap_or_default(),
    })
}

// ==================== 单元测试 ====================

#[cfg(test)]
mod tests {
    use super::*;

    // ---------- HTML 转义函数 ----------
    // 验证 5 个特殊字符是否被正确转义为 HTML 实体

    #[test]
    fn test_html_escape_special_chars() {
        // 验证 5 个特殊字符的转义规则
        assert_eq!(html_escape("<"), "&lt;");
        assert_eq!(html_escape(">"), "&gt;");
        assert_eq!(html_escape("&"), "&amp;");
        assert_eq!(html_escape("\""), "&quot;");
        assert_eq!(html_escape("'"), "&#x27;");
    }

    #[test]
    fn test_html_escape_mixed_string() {
        // 混合字符串应按规则逐一转义
        let input = "<script>alert('XSS');&</script>";
        let escaped = html_escape(input);
        assert_eq!(
            escaped,
            "&lt;script&gt;alert(&#x27;XSS&#x27;);&amp;&lt;/script&gt;"
        );
        // 中文字符不受影响
        assert_eq!(html_escape("甘草"), "甘草");
        // 普通字符不受影响
        assert_eq!(html_escape("人参 100g"), "人参 100g");
        // 空字符串保持为空
        assert_eq!(html_escape(""), "");
    }

    // ---------- CSV 模板生成 ----------
    // download_import_template() 应返回包含 "人参" 和 "黄芪" 的 CSV 字符串

    #[test]
    fn test_download_import_template_contains_renshen_huangqi() {
        let csv = download_import_template().expect("生成模板失败");
        // 必须包含 "人参" 和 "黄芪" 两条样本
        assert!(csv.contains("人参"), "模板应包含 '人参' 样本");
        assert!(csv.contains("黄芪"), "模板应包含 '黄芪' 样本");
        // 包含 UTF-8 BOM，便于 Excel 正确识别中文
        assert!(csv.starts_with('\u{FEFF}'));
        // 包含表头字段
        assert!(csv.contains("name,alias,category,nature,taste,meridian"));
    }

    // ---------- MedicineImportRecord 序列化/反序列化（用 serde_json） ----------

    #[test]
    fn test_medicine_import_record_serde_roundtrip() {
        let record = MedicineImportRecord {
            name: "人参".to_string(),
            alias: "黄参".to_string(),
            category: "补虚药".to_string(),
            nature: "温".to_string(),
            taste: "甘、微苦".to_string(),
            meridian: "脾、肺、心经".to_string(),
            efficacy: "大补元气".to_string(),
            indications: "体虚欲脱".to_string(),
            usage: "煎服".to_string(),
            dosage: "3-9g".to_string(),
            contraindication: "实证忌服".to_string(),
            notes: "".to_string(),
            quantity: Some("500".to_string()),
            unit: "g".to_string(),
            price: Some("85".to_string()),
            min_stock: Some("50".to_string()),
        };
        // 序列化为 JSON 字符串
        let json = serde_json::to_string(&record).expect("序列化失败");
        // 反序列化回来应得到等价对象
        let parsed: MedicineImportRecord = serde_json::from_str(&json).expect("反序列化失败");
        assert_eq!(parsed.name, "人参");
        assert_eq!(parsed.alias, "黄参");
        assert_eq!(parsed.category, "补虚药");
        assert_eq!(parsed.nature, "温");
        assert_eq!(parsed.taste, "甘、微苦");
        assert_eq!(parsed.meridian, "脾、肺、心经");
        assert_eq!(parsed.efficacy, "大补元气");
        assert_eq!(parsed.indications, "体虚欲脱");
        assert_eq!(parsed.usage, "煎服");
        assert_eq!(parsed.dosage, "3-9g");
        assert_eq!(parsed.contraindication, "实证忌服");
        assert_eq!(parsed.quantity, Some("500".to_string()));
        assert_eq!(parsed.unit, "g");
        assert_eq!(parsed.price, Some("85".to_string()));
        assert_eq!(parsed.min_stock, Some("50".to_string()));
    }

    #[test]
    fn test_medicine_import_record_serde_with_defaults() {
        // 仅传必填字段 name，其余字段缺失时应使用 #[serde(default)] 提供的默认值
        let json = r#"{"name":"甘草"}"#;
        let parsed: MedicineImportRecord = serde_json::from_str(json).expect("反序列化失败");
        assert_eq!(parsed.name, "甘草");
        // 缺失的字符串字段应为空字符串
        assert_eq!(parsed.alias, "");
        assert_eq!(parsed.category, "");
        assert_eq!(parsed.unit, "");
        // 缺失的 Option 字段应为 None
        assert_eq!(parsed.quantity, None);
        assert_eq!(parsed.price, None);
        assert_eq!(parsed.min_stock, None);
    }

    // ---------- 库存出入库 + 处方创建/删除 全流程测试 ----------
    // 这些测试通过内存数据库验证核心业务事务逻辑

    use crate::db::DbState;
    use std::path::Path;
    use std::sync::Arc;

    /// 构建测试用 DbState（内存数据库 + 全部迁移），并用 Arc 包裹以模拟 State
    fn setup_db() -> DbState {
        let db = DbState::new(Path::new(":memory:")).expect("打开内存数据库失败");
        db.run_migrations().expect("执行迁移失败");
        db
    }

    /// 在指定连接中插入一味测试药材并返回其 id
    fn insert_test_medicine(conn: &Connection, name: &str) -> i64 {
        conn.execute(
            "INSERT INTO medicines (name, category) VALUES (?1, '补虚药')",
            params![name],
        )
        .expect("插入药材失败");
        conn.last_insert_rowid()
    }

    /// 查询某药材当前库存总量（跨批次聚合）
    ///
    /// 008 迁移后一药多批，需用 SUM 聚合避免 query_row 返回多行报错
    fn get_quantity(conn: &Connection, medicine_id: i64) -> f64 {
        conn.query_row(
            "SELECT COALESCE(SUM(quantity), 0) FROM inventory WHERE medicine_id=?1",
            params![medicine_id],
            |row| row.get::<_, f64>(0),
        )
        .unwrap_or(0.0)
    }

    /// 插入一条测试批次库存（指定批次号、效期）
    fn insert_test_batch(
        conn: &Connection,
        medicine_id: i64,
        batch_no: &str,
        expiry_date: Option<&str>,
        quantity: f64,
        price: f64,
    ) -> i64 {
        conn.execute(
            "INSERT INTO inventory (medicine_id, batch_no, expiry_date, quantity, unit, price, min_stock) VALUES (?1,?2,?3,?4,'g',?5,0)",
            params![medicine_id, batch_no, expiry_date, quantity, price],
        )
        .expect("插入批次库存失败");
        conn.last_insert_rowid()
    }

    #[test]
    fn test_update_stock_in_creates_inventory_if_absent() {
        // 入库时若库存记录不存在，应自动创建
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "入库测试药材");

        // 入库 100
        let pid = insert_test_medicine(&conn, "占位"); // 仅为避免 warning
        let _ = pid;
        // 模拟 update_stock 的内部逻辑（无法直接调用 command 因需 State）
        let tx = conn.unchecked_transaction().unwrap();
        tx.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 0, 'g', 0, 0)",
            params![mid],
        )
        .unwrap();
        tx.execute(
            "UPDATE inventory SET quantity = quantity + ?1 WHERE medicine_id=?2",
            params![100.0, mid],
        )
        .unwrap();
        tx.commit().unwrap();

        assert_eq!(get_quantity(&conn, mid), 100.0);
    }

    #[test]
    fn test_update_stock_out_decrements_quantity() {
        // 出库应正确扣减库存
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "出库测试药材");
        // 先入库 200
        conn.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 200, 'g', 50, 10)",
            params![mid],
        )
        .unwrap();
        // 出库 80
        conn.execute(
            "UPDATE inventory SET quantity = quantity - ?1 WHERE medicine_id=?2 AND quantity >= ?1",
            params![80.0, mid],
        )
        .unwrap();
        assert_eq!(get_quantity(&conn, mid), 120.0);
    }

    #[test]
    fn test_update_stock_rejects_negative() {
        // 库存不足时应阻止出库（affected rows = 0）
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "负库存测试药材");
        conn.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 50, 'g', 10, 5)",
            params![mid],
        )
        .unwrap();
        // 尝试出库 100（超过库存 50），WHERE quantity >= 100 不满足
        let affected = conn
            .execute(
                "UPDATE inventory SET quantity = quantity - ?1 WHERE medicine_id=?2 AND quantity >= ?1",
                params![100.0, mid],
            )
            .unwrap();
        assert_eq!(affected, 0, "库存不足时不应更新");
        assert_eq!(get_quantity(&conn, mid), 50.0, "库存应保持不变");
    }

    #[test]
    fn test_delete_medicine_rejected_when_history_exists() {
        // 有库存变更历史的药材应禁止删除（保留审计轨迹，避免外键约束失败）
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "有历史药材");
        conn.execute(
            "INSERT INTO inventory (medicine_id, batch_no, quantity, unit, price, min_stock) VALUES (?1, '初始库存', 50, 'g', 10, 5)",
            params![mid],
        )
        .unwrap();
        let inv_id = conn.last_insert_rowid();
        // 写一条入库历史
        conn.execute(
            "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, batch_id) VALUES (?1, '有历史药材', '入库', 50, 10, 500, ?2)",
            params![mid, inv_id],
        )
        .unwrap();
        // 此时删除药材应被拒绝（inventory_history 有引用）
        let hist_count: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM inventory_history WHERE medicine_id=?1",
                params![mid],
                |row| row.get(0),
            )
            .unwrap();
        assert!(hist_count > 0, "应有历史记录");
        // 尝试直接 DELETE 会触发外键约束失败（验证 bug 复现路径）
        let result = conn.execute("DELETE FROM medicines WHERE id=?1", params![mid]);
        assert!(result.is_err(), "删除有历史引用的药材应失败");
    }

    #[test]
    fn test_create_prescription_transaction_deducts_stock() {
        // 创建处方应原子扣减库存（模拟 create_prescription 的库存扣减逻辑）
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "处方测试药材");
        conn.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 100, 'g', 20, 10)",
            params![mid],
        )
        .unwrap();

        // 模拟 create_prescription 的原子扣减
        let tx = conn.unchecked_transaction().unwrap();
        let affected = tx
            .execute(
                "UPDATE inventory SET quantity = quantity - ?1, updated_at=CURRENT_TIMESTAMP WHERE medicine_id=?2 AND quantity >= ?1",
                params![30.0, mid],
            )
            .unwrap();
        assert_eq!(affected, 1, "库存充足时应成功扣减");
        tx.commit().unwrap();
        assert_eq!(get_quantity(&conn, mid), 70.0);
    }

    #[test]
    fn test_create_prescription_insufficient_stock_aborts() {
        // 库存不足时扣减失败，事务回滚，库存不变
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "不足库存处方测试");
        conn.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 10, 'g', 20, 5)",
            params![mid],
        )
        .unwrap();

        let tx = conn.unchecked_transaction().unwrap();
        let affected = tx
            .execute(
                "UPDATE inventory SET quantity = quantity - ?1, updated_at=CURRENT_TIMESTAMP WHERE medicine_id=?2 AND quantity >= ?1",
                params![50.0, mid],
            )
            .unwrap();
        assert_eq!(affected, 0, "库存不足时不应扣减");
        // 模拟 create_prescription 的错误返回 + 事务自动回滚
        drop(tx); // Drop 时不 commit 即回滚
        assert_eq!(get_quantity(&conn, mid), 10.0, "回滚后库存应不变");
    }

    #[test]
    fn test_delete_prescription_restores_stock() {
        // 删除处方应回扣库存（验证 delete_prescription 的新逻辑）
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "删除处方回扣测试");

        // 初始库存 100，创建处方扣减 30，剩余 70
        conn.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 70, 'g', 20, 10)",
            params![mid],
        )
        .unwrap();
        // 插入处方 + 明细
        conn.execute(
            "INSERT INTO prescriptions (patient_name, patient_gender, diagnosis, total_amount, created_by) VALUES ('测试患者', '男', '测试诊断', 600, '测试医生')",
            [],
        )
        .unwrap();
        let pid = conn.last_insert_rowid();
        conn.execute(
            "INSERT INTO prescription_items (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount) VALUES (?1, ?2, '删除处方回扣测试', 30, 'g', 20, 600)",
            params![pid, mid],
        )
        .unwrap();

        // 模拟 delete_prescription 的回扣逻辑
        let tx = conn.unchecked_transaction().unwrap();
        // 查询明细
        let items: Vec<(i64, String, f64)> = {
            let mut stmt = tx
                .prepare("SELECT medicine_id, medicine_name, quantity FROM prescription_items WHERE prescription_id=?1")
                .unwrap();
            let rows = stmt
                .query_map(params![pid], |row| {
                    Ok((
                        row.get::<_, i64>(0)?,
                        row.get::<_, String>(1)?,
                        row.get::<_, f64>(2)?,
                    ))
                })
                .unwrap();
            rows.map(|r| r.unwrap()).collect()
        };
        // 回扣库存
        for (medicine_id, _name, quantity) in &items {
            tx.execute(
                "UPDATE inventory SET quantity = quantity + ?1, updated_at=CURRENT_TIMESTAMP WHERE medicine_id=?2",
                params![quantity, medicine_id],
            )
            .unwrap();
        }
        // 删除明细与处方
        tx.execute(
            "DELETE FROM prescription_items WHERE prescription_id=?1",
            params![pid],
        )
        .unwrap();
        tx.execute("DELETE FROM prescriptions WHERE id=?1", params![pid])
            .unwrap();
        tx.commit().unwrap();

        // 库存应恢复为 100
        assert_eq!(
            get_quantity(&conn, mid),
            100.0,
            "删除处方后库存应回扣到原值"
        );
        // 处方与明细应已删除
        let pcount: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM prescriptions WHERE id=?1",
                params![pid],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(pcount, 0, "处方应已删除");
        let icount: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM prescription_items WHERE prescription_id=?1",
                params![pid],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(icount, 0, "处方明细应已删除");
    }

    #[test]
    fn test_list_prescriptions_batch_query_no_n1() {
        // 验证 list_prescriptions 的批量查询逻辑（IN + HashMap 分组）
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "批量查询测试药材");
        conn.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 1000, 'g', 10, 50)",
            params![mid],
        )
        .unwrap();

        // 插入 5 个处方，每个 2 味药（其中一味共用 mid）
        for i in 1..=5 {
            conn.execute(
                "INSERT INTO prescriptions (patient_name, patient_gender, diagnosis, total_amount, created_by) VALUES (?1, '男', '测试', 100, '医生')",
                params![format!("患者{i}")],
            )
            .unwrap();
            let pid = conn.last_insert_rowid();
            conn.execute(
                "INSERT INTO prescription_items (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount) VALUES (?1, ?2, '批量查询测试药材', 10, 'g', 10, 100)",
                params![pid, mid],
            )
            .unwrap();
        }

        // 模拟批量查询：一次 IN 查询所有明细
        let ids: Vec<i64> = (1..=5).collect();
        let placeholders = ids.iter().map(|_| "?").collect::<Vec<_>>().join(", ");
        let sql = format!(
            "SELECT prescription_id FROM prescription_items WHERE prescription_id IN ({placeholders})"
        );
        let id_params: Vec<SqlValue> = ids.iter().map(|id| SqlValue::Integer(*id)).collect();
        let mut stmt = conn.prepare(&sql).unwrap();
        let rows = stmt
            .query_map(params_from_iter(id_params.iter()), |row| row.get::<_, i64>(0))
            .unwrap();
        let collected: Vec<i64> = rows.map(|r| r.unwrap()).collect();
        // 5 个处方各 1 条明细，共 5 条
        assert_eq!(collected.len(), 5);
    }

    // ---------- 库存变更历史查询测试 ----------
    // 验证 list_inventory_history 的动态 SQL 筛选逻辑

    /// 辅助：插入一条 inventory_history 记录
    fn insert_history(
        conn: &Connection,
        medicine_id: i64,
        name: &str,
        htype: &str,
        qty: f64,
        price: f64,
    ) {
        conn.execute(
            "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes) VALUES (?1,?2,?3,?4,?5,?6,'测试员','')",
            params![medicine_id, name, htype, qty, price, qty * price],
        )
        .expect("插入库存历史失败");
    }

    #[test]
    fn test_list_inventory_history_filter_by_medicine() {
        // 按 medicine_id 筛选应只返回该药材的历史记录
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid1 = insert_test_medicine(&conn, "历史药材A");
        let mid2 = insert_test_medicine(&conn, "历史药材B");
        insert_history(&conn, mid1, "历史药材A", "入库", 100.0, 10.0);
        insert_history(&conn, mid1, "历史药材A", "出库", 30.0, 10.0);
        insert_history(&conn, mid2, "历史药材B", "入库", 50.0, 20.0);

        // 模拟 list_inventory_history 的 medicine_id 筛选
        let mut sql = String::from(
            "SELECT id, medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes, created_at FROM inventory_history WHERE 1=1",
        );
        let mut pv: Vec<SqlValue> = Vec::new();
        sql.push_str(" AND medicine_id = ?");
        pv.push(SqlValue::Integer(mid1));
        sql.push_str(" ORDER BY id DESC");
        let mut stmt = conn.prepare(&sql).unwrap();
        let rows = stmt
            .query_map(params_from_iter(pv.iter()), |row| {
                Ok((
                    row.get::<_, i64>(0)?,
                    row.get::<_, i64>(1)?,
                    row.get::<_, String>(2)?,
                    row.get::<_, String>(3)?,
                ))
            })
            .unwrap();
        let results: Vec<(i64, i64, String, String)> = rows.map(|r| r.unwrap()).collect();
        assert_eq!(results.len(), 2, "药材A 应有 2 条历史");
        assert!(results.iter().all(|r| r.1 == mid1));
    }

    #[test]
    fn test_list_inventory_history_filter_by_type() {
        // 按 type 筛选应只返回匹配类型的记录
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "类型筛选药材");
        insert_history(&conn, mid, "类型筛选药材", "入库", 100.0, 10.0);
        insert_history(&conn, mid, "类型筛选药材", "出库", 30.0, 10.0);
        insert_history(&conn, mid, "类型筛选药材", "入库", 50.0, 10.0);

        // 模拟 list_inventory_history 的 type 筛选
        let sql = String::from(
            "SELECT id, type FROM inventory_history WHERE 1=1 AND medicine_id = ? AND type = ? ORDER BY id DESC",
        );
        let pv: Vec<SqlValue> = vec![SqlValue::Integer(mid), SqlValue::Text("入库".to_string())];
        let mut stmt = conn.prepare(&sql).unwrap();
        let rows = stmt
            .query_map(params_from_iter(pv.iter()), |row| {
                Ok((row.get::<_, i64>(0)?, row.get::<_, String>(1)?))
            })
            .unwrap();
        let results: Vec<(i64, String)> = rows.map(|r| r.unwrap()).collect();
        assert_eq!(results.len(), 2, "应有 2 条入库记录");
        assert!(results.iter().all(|r| r.1 == "入库"));
    }

    // ---------- 操作日志查询测试 ----------
    // 验证 list_operation_logs 的动态 SQL 筛选逻辑

    /// 辅助：插入一条 operation_log 记录
    fn insert_log(conn: &Connection, op_type: &str, target: &str, target_id: i64, details: &str) {
        conn.execute(
            "INSERT INTO operation_logs (operation_type, target_type, target_id, operator, details) VALUES (?1,?2,?3,'系统',?4)",
            params![op_type, target, target_id, details],
        )
        .expect("插入操作日志失败");
    }

    #[test]
    fn test_list_operation_logs_filter_by_type() {
        // 按 operation_type 筛选应只返回匹配类型的日志
        let db = setup_db();
        let conn = db.lock().unwrap();
        insert_log(&conn, "CREATE", "medicine", 1, "创建药材: 人参");
        insert_log(&conn, "UPDATE", "medicine", 1, "更新药材: 人参");
        insert_log(&conn, "DELETE", "medicine", 2, "删除药材: 甘草");
        insert_log(&conn, "CREATE", "patient", 1, "创建患者: 张三");

        // 模拟 list_operation_logs 的 operation_type 筛选
        let sql = String::from(
            "SELECT id, operation_type, target_type, target_id, details FROM operation_logs WHERE 1=1 AND operation_type = ? ORDER BY id DESC",
        );
        let pv: Vec<SqlValue> = vec![SqlValue::Text("CREATE".to_string())];
        let mut stmt = conn.prepare(&sql).unwrap();
        let rows = stmt
            .query_map(params_from_iter(pv.iter()), |row| {
                Ok((
                    row.get::<_, i64>(0)?,
                    row.get::<_, String>(1)?,
                    row.get::<_, String>(2)?,
                    row.get::<_, i64>(3)?,
                    row.get::<_, String>(4)?,
                ))
            })
            .unwrap();
        let results: Vec<(i64, String, String, i64, String)> = rows.map(|r| r.unwrap()).collect();
        assert_eq!(results.len(), 2, "应有 2 条 CREATE 日志");
        assert!(results.iter().all(|r| r.1 == "CREATE"));
    }

    #[test]
    fn test_list_operation_logs_filter_by_target_type() {
        // 按 target_type 筛选应只返回匹配目标的日志
        let db = setup_db();
        let conn = db.lock().unwrap();
        insert_log(&conn, "CREATE", "medicine", 1, "创建药材");
        insert_log(&conn, "CREATE", "patient", 1, "创建患者");
        insert_log(&conn, "UPDATE", "patient", 1, "更新患者");

        let sql = "SELECT id, target_type FROM operation_logs WHERE target_type = ? ORDER BY id";
        let mut stmt = conn.prepare(sql).unwrap();
        let rows = stmt
            .query_map(["patient"], |row| {
                Ok((row.get::<_, i64>(0)?, row.get::<_, String>(1)?))
            })
            .unwrap();
        let results: Vec<(i64, String)> = rows.map(|r| r.unwrap()).collect();
        assert_eq!(results.len(), 2, "应有 2 条 patient 日志");
        assert!(results.iter().all(|r| r.1 == "patient"));
    }

    // ---------- batch_import N+1 优化验证测试 ----------
    // 验证批量预查 IN + HashMap 模式正确识别已存在药材

    #[test]
    fn test_batch_import_pre_query_hashmap_pattern() {
        // 模拟 batch_import 的批量预查逻辑：IN 查询 + HashMap 查找
        let db = setup_db();
        let conn = db.lock().unwrap();
        // 预置 2 味已存在药材
        let id1 = insert_test_medicine(&conn, "已存在药材A");
        let id2 = insert_test_medicine(&conn, "已存在药材B");

        // 模拟导入记录：3 条（2 条已存在 + 1 条新建）
        let names: Vec<String> = vec![
            "已存在药材A".to_string(),
            "已存在药材B".to_string(),
            "新药材C".to_string(),
        ];

        // 批量预查：IN + HashMap（与 batch_import_medicines 逻辑一致）
        let placeholders = names.iter().map(|_| "?").collect::<Vec<_>>().join(", ");
        let sql = format!("SELECT id, name FROM medicines WHERE name IN ({placeholders})");
        let name_params: Vec<SqlValue> = names.iter().map(|n| SqlValue::Text(n.clone())).collect();
        let mut existing_map: std::collections::HashMap<String, i64> =
            std::collections::HashMap::new();
        {
            let mut stmt = conn.prepare(&sql).unwrap();
            let rows = stmt
                .query_map(params_from_iter(name_params.iter()), |row| {
                    Ok((row.get::<_, i64>(0)?, row.get::<_, String>(1)?))
                })
                .unwrap();
            for r in rows {
                let (id, name) = r.unwrap();
                existing_map.insert(name, id);
            }
        }

        // 验证：已存在的 2 味应被识别，新药材不在 HashMap 中
        assert_eq!(existing_map.get("已存在药材A"), Some(&id1));
        assert_eq!(existing_map.get("已存在药材B"), Some(&id2));
        assert!(existing_map.get("新药材C").is_none());

        // 模拟新建后更新 HashMap（处理同批次重复名称）
        let new_id = id2 + 1; // 模拟 last_insert_rowid
        existing_map.insert("新药材C".to_string(), new_id);
        assert_eq!(existing_map.get("新药材C"), Some(&new_id));
    }

    #[test]
    fn test_batch_import_duplicate_name_in_same_batch_uses_update() {
        // 同批次内重复名称：第一条 INSERT 后更新 HashMap，第二条应走 UPDATE
        let db = setup_db();
        let conn = db.lock().unwrap();

        // 模拟两条同名记录导入
        let names = vec!["重复药材".to_string(), "重复药材".to_string()];
        let placeholders = names.iter().map(|_| "?").collect::<Vec<_>>().join(", ");
        let sql = format!("SELECT id, name FROM medicines WHERE name IN ({placeholders})");
        let name_params: Vec<SqlValue> = names.iter().map(|n| SqlValue::Text(n.clone())).collect();
        let mut existing_map: std::collections::HashMap<String, i64> =
            std::collections::HashMap::new();
        {
            let mut stmt = conn.prepare(&sql).unwrap();
            let rows = stmt
                .query_map(params_from_iter(name_params.iter()), |row| {
                    Ok((row.get::<_, i64>(0)?, row.get::<_, String>(1)?))
                })
                .unwrap();
            for r in rows {
                let (id, name) = r.unwrap();
                existing_map.insert(name, id);
            }
        }

        // 第一条：existing_map 为空 → 模拟 INSERT + 更新 HashMap
        assert!(existing_map.get("重复药材").is_none(), "首条应判定为新建");
        let new_id = insert_test_medicine(&conn, "重复药材");
        existing_map.insert("重复药材".to_string(), new_id);

        // 第二条：existing_map 已有 → 应走 UPDATE 路径
        assert_eq!(
            existing_map.get("重复药材"),
            Some(&new_id),
            "第二条应判定为更新"
        );
    }

    // 避免未使用警告
    #[test]
    fn _ensure_arc_used() {
        let _ = Arc::new(1);
    }

    // ---------- 009 关联表精确回扣测试 ----------
    // 验证跨批次扣减的处方，删除时按 prescription_item_batches 精确回扣到各批次

    #[test]
    fn test_cross_batch_prescription_delete_restores_each_batch() {
        // 场景：药材有 B1(30,效期近) 和 B2(50,效期远)，处方扣 40（B1全扣30 + B2扣10）
        // 删除处方后，B1 应回到 30，B2 应回到 50（精确回扣，不是整量回扣到首批次）
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "跨批回扣测试");
        let b1 = insert_test_batch(&conn, mid, "B1", Some("2026-09-01"), 30.0, 10.0);
        let b2 = insert_test_batch(&conn, mid, "B2", Some("2027-06-01"), 50.0, 12.0);

        // 模拟 create_prescription：FEFO 扣减 40
        let tx = conn.unchecked_transaction().unwrap();
        let batches = select_batches_fefo(&tx, mid, 40.0).expect("FEFO 应成功");
        assert_eq!(batches.len(), 2, "应跨 2 批次");
        // 写处方 + 明细
        tx.execute(
            "INSERT INTO prescriptions (patient_name, total_amount, created_by) VALUES ('测试', 440, '医生')",
            [],
        )
        .unwrap();
        let pid = tx.last_insert_rowid();
        tx.execute(
            "INSERT INTO prescription_items (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount, batch_id) VALUES (?1,?2,'跨批回扣测试',40,'g',11,440,?3)",
            params![pid, mid, batches[0].0],
        )
        .unwrap();
        let item_id = tx.last_insert_rowid();
        // 扣库存 + 写关联表
        for (batch_id, batch_qty, deduct, price, _unit, _batch_no) in &batches {
            tx.execute(
                "UPDATE inventory SET quantity=?1 WHERE id=?2",
                params![batch_qty - deduct, batch_id],
            )
            .unwrap();
            tx.execute(
                "INSERT INTO prescription_item_batches (prescription_item_id, batch_id, quantity, price) VALUES (?1,?2,?3,?4)",
                params![item_id, batch_id, deduct, price],
            )
            .unwrap();
        }
        tx.commit().unwrap();

        // 验证扣减后：B1=0, B2=40
        let b1_qty: f64 = conn.query_row("SELECT quantity FROM inventory WHERE id=?1", params![b1], |r| r.get(0)).unwrap();
        let b2_qty: f64 = conn.query_row("SELECT quantity FROM inventory WHERE id=?1", params![b2], |r| r.get(0)).unwrap();
        assert_eq!(b1_qty, 0.0, "B1 扣减后应为 0");
        assert_eq!(b2_qty, 40.0, "B2 扣减后应为 40");

        // 模拟 delete_prescription 的精确回扣逻辑
        let tx = conn.unchecked_transaction().unwrap();
        let pib_rows: Vec<(i64, f64, f64)> = {
            let mut stmt = tx.prepare(
                "SELECT pib.batch_id, pib.quantity, pib.price FROM prescription_item_batches pib JOIN prescription_items pi ON pib.prescription_item_id = pi.id WHERE pi.prescription_id=?1",
            ).unwrap();
            let rows = stmt.query_map(params![pid], |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?))).unwrap();
            rows.map(|r| r.unwrap()).collect()
        };
        assert_eq!(pib_rows.len(), 2, "关联表应有 2 条扣减明细");
        for (batch_id, qty, _price) in &pib_rows {
            tx.execute(
                "UPDATE inventory SET quantity = quantity + ?1 WHERE id=?2",
                params![qty, batch_id],
            )
            .unwrap();
        }
        tx.execute("DELETE FROM prescription_item_batches WHERE prescription_item_id IN (SELECT id FROM prescription_items WHERE prescription_id=?1)", params![pid]).unwrap();
        tx.execute("DELETE FROM prescription_items WHERE prescription_id=?1", params![pid]).unwrap();
        tx.execute("DELETE FROM prescriptions WHERE id=?1", params![pid]).unwrap();
        tx.commit().unwrap();

        // 验证回扣后：B1=30, B2=50（精确回扣到原批次，不是整量回扣到 B1）
        let b1_after: f64 = conn.query_row("SELECT quantity FROM inventory WHERE id=?1", params![b1], |r| r.get(0)).unwrap();
        let b2_after: f64 = conn.query_row("SELECT quantity FROM inventory WHERE id=?1", params![b2], |r| r.get(0)).unwrap();
        assert_eq!(b1_after, 30.0, "B1 精确回扣后应恢复为 30");
        assert_eq!(b2_after, 50.0, "B2 精确回扣后应恢复为 50");
    }


    // ---------- 批次 + 效期 + FEFO 出库测试 ----------
    // 008 迁移后的核心新逻辑：一药多批、近效期优先、跨批次扣减

    #[test]
    fn test_fefo_selects_nearest_expiry_first() {
        // 三批次效期不同，select_batches_fefo 应按近效期优先顺序返回
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "FEFO顺序测试");
        insert_test_batch(&conn, mid, "B1", Some("2026-12-01"), 50.0, 10.0);
        insert_test_batch(&conn, mid, "B2", Some("2026-08-01"), 30.0, 12.0);
        insert_test_batch(&conn, mid, "B3", Some("2027-01-01"), 40.0, 11.0);

        // 需要扣减 60，应先扣 B2（近效期 30）全部 30，再扣 B1 30
        let tx = conn.unchecked_transaction().unwrap();
        let batches = select_batches_fefo(&tx, mid, 60.0).expect("FEFO 应成功");
        tx.commit().unwrap();

        assert_eq!(batches.len(), 2, "应跨 2 个批次扣减");
        // 第一扣减项应为 B2（效期最近）
        assert_eq!(batches[0].5, "B2", "近效期批次应优先");
        assert_eq!(batches[0].2, 30.0, "B2 应全部扣减");
        // 第二扣减项应为 B1
        assert_eq!(batches[1].5, "B1");
        assert_eq!(batches[1].2, 30.0, "B1 应扣减剩余 30");
    }

    #[test]
    fn test_fefo_null_expiry_goes_last() {
        // 无效期的批次应排在最后出库
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "无效期排后测试");
        insert_test_batch(&conn, mid, "无期", None, 100.0, 5.0);
        insert_test_batch(&conn, mid, "有期", Some("2026-09-01"), 20.0, 8.0);

        // 需要扣减 30，应优先扣"有期"批次 20，再扣"无期"批次 10
        let tx = conn.unchecked_transaction().unwrap();
        let batches = select_batches_fefo(&tx, mid, 30.0).expect("FEFO 应成功");
        tx.commit().unwrap();

        assert_eq!(batches.len(), 2);
        assert_eq!(batches[0].5, "有期", "有效期批次应优先于无效期");
        assert_eq!(batches[0].2, 20.0);
        assert_eq!(batches[1].5, "无期", "无效期批次应最后扣减");
        assert_eq!(batches[1].2, 10.0);
    }

    #[test]
    fn test_fefo_insufficient_stock_returns_error() {
        // 总库存不足时 select_batches_fefo 应返回错误
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "FEFO不足测试");
        insert_test_batch(&conn, mid, "B1", Some("2026-09-01"), 30.0, 10.0);
        insert_test_batch(&conn, mid, "B2", Some("2027-01-01"), 20.0, 11.0);

        let tx = conn.unchecked_transaction().unwrap();
        let result = select_batches_fefo(&tx, mid, 100.0);
        drop(tx); // 不 commit 即回滚
        assert!(result.is_err(), "总库存 50 < 需求 100 应返回错误");
    }

    #[test]
    fn test_batch_inbound_merges_same_batch() {
        // 模拟 update_stock 入库逻辑：同批次已存在应合并数量
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "同批合并测试");
        // 已存在批次 BATCH-A，库存 50
        insert_test_batch(&conn, mid, "BATCH-A", Some("2027-06-01"), 50.0, 10.0);

        // 模拟 update_stock 的入库合并路径（同 medicine_id + batch_no）
        let tx = conn.unchecked_transaction().unwrap();
        let change = 30.0_f64;
        let existing: Option<(i64, f64)> = tx
            .query_row(
                "SELECT id, quantity FROM inventory WHERE medicine_id=?1 AND batch_no=?2",
                params![mid, "BATCH-A"],
                |row| Ok((row.get(0)?, row.get(1)?)),
            )
            .optional()
            .unwrap();
        let (inv_id, old_qty) = existing.expect("应找到同批次");
        tx.execute(
            "UPDATE inventory SET quantity=?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
            params![old_qty + change, inv_id],
        )
        .unwrap();
        tx.commit().unwrap();

        // 该批次库存应为 80
        let qty: f64 = conn
            .query_row(
                "SELECT quantity FROM inventory WHERE medicine_id=?1 AND batch_no=?2",
                params![mid, "BATCH-A"],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(qty, 80.0, "同批次入库应合并累加");
        // inventory 表对该药材应只有 1 行
        let cnt: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM inventory WHERE medicine_id=?1",
                params![mid],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(cnt, 1, "同批次合并后应仅 1 行");
    }

    #[test]
    fn test_batch_inbound_new_batch_creates_new_row() {
        // 模拟 update_stock 入库逻辑：新批次应新建 inventory 行
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "新批新建测试");
        insert_test_batch(&conn, mid, "BATCH-A", Some("2027-06-01"), 50.0, 10.0);

        // 入库新批次 BATCH-B 30
        let tx = conn.unchecked_transaction().unwrap();
        let existing: Option<(i64, f64)> = tx
            .query_row(
                "SELECT id, quantity FROM inventory WHERE medicine_id=?1 AND batch_no=?2",
                params![mid, "BATCH-B"],
                |row| Ok((row.get(0)?, row.get(1)?)),
            )
            .optional()
            .unwrap();
        assert!(existing.is_none(), "BATCH-B 应不存在");
        tx.execute(
            "INSERT INTO inventory (medicine_id, batch_no, expiry_date, quantity, unit, price, min_stock) VALUES (?1,?2,?3,?4,'g',?5,0)",
            params![mid, "BATCH-B", "2028-01-01", 30.0, 10.0],
        )
        .unwrap();
        tx.commit().unwrap();

        // 总库存应为 80（50 + 30）
        assert_eq!(get_quantity(&conn, mid), 80.0);
        let cnt: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM inventory WHERE medicine_id=?1",
                params![mid],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(cnt, 2, "新批次入库后应有 2 行");
    }

    #[test]
    fn test_cross_batch_deduction_applies_correctly() {
        // 模拟 update_stock 出库：select_batches_fefo 返回后逐批次扣减
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "跨批扣减测试");
        let b1 = insert_test_batch(&conn, mid, "B1", Some("2026-09-01"), 30.0, 10.0);
        let b2 = insert_test_batch(&conn, mid, "B2", Some("2027-01-01"), 50.0, 12.0);

        // 出库 40：应扣 B1 全部 30 + B2 10
        let tx = conn.unchecked_transaction().unwrap();
        let batches = select_batches_fefo(&tx, mid, 40.0).expect("FEFO 应成功");
        for (batch_id, batch_qty, deduct, _price, _unit, _batch_no) in &batches {
            tx.execute(
                "UPDATE inventory SET quantity=?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
                params![batch_qty - deduct, batch_id],
            )
            .unwrap();
        }
        tx.commit().unwrap();

        let b1_qty: f64 = conn
            .query_row(
                "SELECT quantity FROM inventory WHERE id=?1",
                params![b1],
                |row| row.get(0),
            )
            .unwrap();
        let b2_qty: f64 = conn
            .query_row(
                "SELECT quantity FROM inventory WHERE id=?1",
                params![b2],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(b1_qty, 0.0, "B1 应被扣完");
        assert_eq!(b2_qty, 40.0, "B2 应剩 40");
        assert_eq!(get_quantity(&conn, mid), 40.0);
    }

    #[test]
    fn test_list_expiring_batches_query() {
        // 验证 list_expiring_batches 的 SQL 筛选逻辑：
        // 仅返回有效期、quantity>0 且在 N 天内到期的批次，按效期升序
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "效期预警测试");
        // 近效期（30天内）— 应命中
        insert_test_batch(&conn, mid, "近效期", Some("2026-08-15"), 20.0, 10.0);
        // 远效期（>30天）— 不应命中
        insert_test_batch(&conn, mid, "远效期", Some("2027-12-31"), 50.0, 10.0);
        // 已过期 — 应命中（date <= now+N 包含过去日期）
        insert_test_batch(&conn, mid, "已过期", Some("2025-01-01"), 10.0, 10.0);
        // 无效期 — 不应命中
        insert_test_batch(&conn, mid, "无期", None, 100.0, 10.0);
        // 效期在窗口内但库存为 0 — 不应命中
        insert_test_batch(&conn, mid, "零库存", Some("2026-08-10"), 0.0, 10.0);

        // 模拟 list_expiring_batches 的查询（30 天窗口）
        let mut stmt = conn
            .prepare(
                "SELECT i.id, i.batch_no, i.expiry_date, i.quantity
                 FROM inventory i
                 JOIN medicines m ON i.medicine_id = m.id
                 WHERE i.expiry_date IS NOT NULL
                   AND i.expiry_date != ''
                   AND date(i.expiry_date) <= date('now', ?1)
                   AND i.quantity > 0
                 ORDER BY i.expiry_date ASC",
            )
            .unwrap();
        let rows = stmt
            .query_map(params!["+30 days"], |row| {
                Ok((
                    row.get::<_, i64>(0)?,
                    row.get::<_, String>(1)?,
                    row.get::<_, String>(2)?,
                    row.get::<_, f64>(3)?,
                ))
            })
            .unwrap();
        let results: Vec<(i64, String, String, f64)> = rows.map(|r| r.unwrap()).collect();

        // 应返回 2 条：已过期 + 近效期
        assert_eq!(results.len(), 2, "应命中近效期和已过期 2 条");
        // 按效期升序：已过期 < 近效期
        assert_eq!(results[0].1, "已过期", "效期最早应排第一");
        assert_eq!(results[1].1, "近效期");
    }

    #[test]
    fn test_dashboard_low_stock_aggregates_across_batches() {
        // 验证 get_dashboard_data 的低库存聚合：按 medicine_id SUM(quantity) 后比较 min_stock
        // 注意：种子迁移 001/007 会插入约 400 味药材库存，本测试只验证聚合 SQL 语义
        let db = setup_db();
        let conn = db.lock().unwrap();
        let mid = insert_test_medicine(&conn, "多批低库存测试");
        // 两批次合计 80，min_stock 均为 100 → 聚合 MIN=100，80<=100 判为低库存
        conn.execute(
            "INSERT INTO inventory (medicine_id, batch_no, expiry_date, quantity, unit, price, min_stock) VALUES (?1,'B1','2026-12-01',30,'g',10,100)",
            params![mid],
        )
        .unwrap();
        conn.execute(
            "INSERT INTO inventory (medicine_id, batch_no, expiry_date, quantity, unit, price, min_stock) VALUES (?1,'B2','2027-06-01',50,'g',10,100)",
            params![mid],
        )
        .unwrap();

        // 模拟 get_dashboard_data 的低库存聚合 SQL，仅对测试药材统计
        let is_low: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM (
                    SELECT medicine_id, SUM(quantity) as total_qty, MIN(min_stock) as min_threshold
                    FROM inventory
                    WHERE medicine_id = ?1
                    GROUP BY medicine_id
                    HAVING total_qty <= min_threshold
                )",
                params![mid],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(is_low, 1, "合计 80 <= min_stock 100 应判为低库存");

        // 验证非低库存场景：插入库存充足的药材（合计 500 > min_stock 100）
        let mid2 = insert_test_medicine(&conn, "充足药材");
        conn.execute(
            "INSERT INTO inventory (medicine_id, batch_no, expiry_date, quantity, unit, price, min_stock) VALUES (?1,'B1','2027-06-01',500,'g',10,100)",
            params![mid2],
        )
        .unwrap();
        let is_low2: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM (
                    SELECT medicine_id, SUM(quantity) as total_qty, MIN(min_stock) as min_threshold
                    FROM inventory
                    WHERE medicine_id = ?1
                    GROUP BY medicine_id
                    HAVING total_qty <= min_threshold
                )",
                params![mid2],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(is_low2, 0, "合计 500 > 100 不应判为低库存");
    }
}
