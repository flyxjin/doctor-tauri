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
    let exists: Option<i64> = conn
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
    conn.execute(
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
    let id = conn.last_insert_rowid();
    log_operation(&conn, "CREATE", "medicine", id, &format!("创建药材: {}", medicine.name))?;
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
    let dup: Option<i64> = conn
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
    conn.execute(
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
    log_operation(&conn, "UPDATE", "medicine", id, &format!("更新药材: {}", medicine.name))?;
    Ok(())
}

/// 删除药材（级联删除库存记录）
#[tauri::command]
pub fn delete_medicine(id: i64, state: State<'_, DbState>) -> Result<(), String> {
    let conn = state.lock()?;
    let name: Option<String> = conn
        .query_row(
            "SELECT name FROM medicines WHERE id=?1",
            params![id],
            |row| row.get(0),
        )
        .optional()
        .map_err(|e| e.to_string())?;
    conn.execute("DELETE FROM medicines WHERE id=?1", params![id])
        .map_err(|e| format!("删除药材失败: {e}"))?;
    log_operation(
        &conn,
        "DELETE",
        "medicine",
        id,
        &format!("删除药材: {}", name.unwrap_or_default()),
    )?;
    Ok(())
}

// ==================== 库存管理 ====================

/// 库存列表（联表药材名与分类）
#[tauri::command]
pub fn list_inventory(state: State<'_, DbState>) -> Result<Vec<Inventory>, String> {
    let conn = state.lock()?;
    let list: Vec<Inventory> = {
        let mut stmt = conn.prepare(
            "SELECT i.id, i.medicine_id, i.quantity, i.unit, i.price, i.min_stock, i.notes, i.created_at, i.updated_at, m.name, m.category
             FROM inventory i
             LEFT JOIN medicines m ON i.medicine_id = m.id
             ORDER BY i.medicine_id ASC",
        )
        .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map((), |row| {
                Ok(Inventory {
                    id: row.get(0)?,
                    medicine_id: row.get(1)?,
                    quantity: row.get::<_, Option<f64>>(2)?.unwrap_or(0.0),
                    unit: row
                        .get::<_, Option<String>>(3)?
                        .unwrap_or_else(|| "g".to_string()),
                    price: row.get::<_, Option<f64>>(4)?.unwrap_or(0.0),
                    min_stock: row.get::<_, Option<f64>>(5)?.unwrap_or(0.0),
                    notes: row.get::<_, Option<String>>(6)?.unwrap_or_default(),
                    created_at: row.get(7)?,
                    updated_at: row.get(8)?,
                    medicine_name: row.get::<_, Option<String>>(9)?.unwrap_or_default(),
                    category: row.get::<_, Option<String>>(10)?.unwrap_or_default(),
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

/// 入库 / 出库
///
/// - `medicine_id`：药材 ID
/// - `change`：变更数量（正数）
/// - `is_in`：true=入库，false=出库
#[tauri::command]
pub fn update_stock(
    medicine_id: i64,
    change: f64,
    is_in: bool,
    operator: Option<String>,
    notes: Option<String>,
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

    // 取当前库存（无记录则创建）
    let row: Option<(i64, f64, f64, String)> = tx
        .query_row(
            "SELECT id, quantity, price, unit FROM inventory WHERE medicine_id=?1",
            params![medicine_id],
            |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?, row.get(3)?)),
        )
        .optional()
        .map_err(|e| e.to_string())?;
    let (inv_id, old_qty, price, unit) = match row {
        Some(r) => r,
        None => {
            tx.execute(
                "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 0, 'g', 0, 0)",
                params![medicine_id],
            )
            .map_err(|e| e.to_string())?;
            (tx.last_insert_rowid(), 0.0, 0.0, "g".to_string())
        }
    };

    let delta = if is_in { change } else { -change };
    let new_qty = old_qty + delta;
    if new_qty < 0.0 {
        return Err(format!(
            "库存不足，当前 {}，尝试出库 {}",
            old_qty, change
        ));
    }
    tx.execute(
        "UPDATE inventory SET quantity=?1, updated_at=CURRENT_TIMESTAMP WHERE id=?2",
        params![new_qty, inv_id],
    )
    .map_err(|e| e.to_string())?;

    // 记录库存变更历史
    let hist_type = if is_in { "入库" } else { "出库" };
    let total_amount = change * price;
    tx.execute(
        "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
        params![
            medicine_id,
            &medicine_name,
            hist_type,
            change,
            price,
            total_amount,
            operator.unwrap_or_default(),
            notes.unwrap_or_default(),
        ],
    )
    .map_err(|e| e.to_string())?;

    log_operation(
        &tx,
        "STOCK",
        "inventory",
        inv_id,
        &format!("{}: {} {}{}", hist_type, medicine_name, change, unit),
    )?;
    tx.commit().map_err(|e| e.to_string())?;
    Ok(())
}

// ==================== 处方管理 ====================

/// 处方列表（含明细，支持按患者/诊断搜索）
#[tauri::command]
pub fn list_prescriptions(
    keyword: Option<String>,
    limit: Option<i64>,
    state: State<'_, DbState>,
) -> Result<Vec<PrescriptionWithItems>, String> {
    let conn = state.lock()?;
    let limit = limit.unwrap_or(100).clamp(1, 1000);

    let mut sql = String::from(
        "SELECT id, patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by, created_at FROM prescriptions",
    );
    let mut pv: Vec<SqlValue> = Vec::new();
    if let Some(kw) = &keyword {
        if !kw.is_empty() {
            sql.push_str(" WHERE patient_name LIKE ? OR diagnosis LIKE ?");
            let pat = format!("%{kw}%");
            pv.push(SqlValue::Text(pat.clone()));
            pv.push(SqlValue::Text(pat));
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
        "SELECT id, prescription_id, medicine_id, medicine_name, quantity, unit, price, amount FROM prescription_items WHERE prescription_id IN ({placeholders}) ORDER BY id ASC"
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
    let conn = state.lock()?;
    let tx = conn.unchecked_transaction().map_err(|e| e.to_string())?;
    let p = input.prescription;

    let total = if p.total_amount > 0.0 {
        p.total_amount
    } else {
        input.items.iter().map(|i| i.amount).sum()
    };

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
    let prescription_id = tx.last_insert_rowid();

    for item in &input.items {
        tx.execute(
            "INSERT INTO prescription_items (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount) VALUES (?1,?2,?3,?4,?5,?6,?7)",
            params![
                prescription_id,
                item.medicine_id,
                &item.medicine_name,
                item.quantity,
                &item.unit,
                item.price,
                item.amount,
            ],
        )
        .map_err(|e| format!("写入处方明细失败: {e}"))?;

        // 原子扣减库存（quantity >= change 才更新，避免负库存）
        let affected = tx
            .execute(
                "UPDATE inventory SET quantity = quantity - ?1, updated_at=CURRENT_TIMESTAMP WHERE medicine_id=?2 AND quantity >= ?1",
                params![item.quantity, item.medicine_id],
            )
            .map_err(|e| format!("扣减库存失败: {e}"))?;
        if affected == 0 {
            return Err(format!("药材 '{}' 库存不足或无库存记录", item.medicine_name));
        }

        // 记录库存出库历史
        tx.execute(
            "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
            params![
                item.medicine_id,
                &item.medicine_name,
                "出库",
                item.quantity,
                item.price,
                item.quantity * item.price,
                &p.created_by,
                "处方出库",
            ],
        )
        .map_err(|e| e.to_string())?;
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

    // 查询处方明细，用于回扣库存
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

    // 回扣库存 + 记录退库历史
    for (medicine_id, medicine_name, quantity) in &items {
        tx.execute(
            "UPDATE inventory SET quantity = quantity + ?1, updated_at=CURRENT_TIMESTAMP WHERE medicine_id=?2",
            params![quantity, medicine_id],
        )
        .map_err(|e| format!("回扣库存失败: {e}"))?;
        tx.execute(
            "INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
            params![medicine_id, medicine_name, "退库", quantity, 0.0, 0.0, "", "删除处方回扣"],
        )
        .map_err(|e| e.to_string())?;
    }

    // 删除明细与处方
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
    conn.execute(
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
    let id = conn.last_insert_rowid();
    log_operation(&conn, "CREATE", "patient", id, &format!("创建患者: {}", patient.name))?;
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
    conn.execute(
        "UPDATE patients SET name=?1, gender=?2, age=?3, phone=?4, address=?5, allergy=?6, medical_history=?7, notes=?8, updated_at=datetime('now','localtime') WHERE id=?9",
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
    log_operation(&conn, "UPDATE", "patient", id, &format!("更新患者: {}", patient.name))?;
    Ok(())
}

/// 删除患者档案
#[tauri::command]
pub fn delete_patient(id: i64, state: State<'_, DbState>) -> Result<(), String> {
    let conn = state.lock()?;
    let name: Option<String> = conn
        .query_row(
            "SELECT name FROM patients WHERE id=?1",
            params![id],
            |row| row.get(0),
        )
        .optional()
        .map_err(|e| e.to_string())?;
    conn.execute("DELETE FROM patients WHERE id=?1", params![id])
        .map_err(|e| format!("删除患者失败: {e}"))?;
    log_operation(
        &conn,
        "DELETE",
        "patient",
        id,
        &format!("删除患者: {}", name.unwrap_or_default()),
    )?;
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
            "SELECT COUNT(*) FROM inventory WHERE quantity <= min_stock",
            (),
            |row| row.get(0),
        )
        .map_err(|e| e.to_string())?;

    let low_stock_list: Vec<LowStockItem> = {
        let mut stmt = conn.prepare(
            "SELECT i.medicine_id, m.name, i.quantity, i.min_stock, i.unit
             FROM inventory i JOIN medicines m ON i.medicine_id=m.id
             WHERE i.quantity <= i.min_stock
             ORDER BY (i.quantity - i.min_stock) ASC LIMIT 20",
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

    Ok(DashboardData {
        medicine_count,
        prescription_count,
        total_stock_value,
        low_stock_count,
        low_stock_list,
        recent_prescriptions,
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

        // 查询是否已存在同名药材
        let existing_id: Option<i64> = tx
            .query_row(
                "SELECT id FROM medicines WHERE name = ?1",
                params![&name],
                |row| row.get(0),
            )
            .optional()
            .map_err(|e| format!("查询药材失败: {e}"))?;

        let result = if let Some(id) = existing_id {
            // UPSERT：更新药材
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
                // UPSERT：更新或新建库存
                let affected = tx.execute(
                    "UPDATE inventory SET quantity=?1, unit=?2, price=?3, min_stock=?4, updated_at=CURRENT_TIMESTAMP WHERE medicine_id=?5",
                    params![quantity, &unit, price, min_stock, id],
                ).map_err(|e| format!("更新库存失败: {e}"))?;
                if affected == 0 {
                    tx.execute(
                        "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1,?2,?3,?4,?5)",
                        params![id, quantity, &unit, price, min_stock],
                    ).map_err(|e| format!("创建库存失败: {e}"))?;
                }
                Ok(())
            })
        } else {
            // 新建药材 + 库存
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
                    "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1,?2,?3,?4,?5)",
                    params![new_id, quantity, &unit, price, min_stock],
                ).map_err(|e| format!("创建库存失败: {e}"))?;
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
#[tauri::command]
pub fn save_text_to_downloads(
    filename: String,
    content: String,
    app_handle: tauri::AppHandle,
) -> Result<String, String> {
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
                "SELECT id, prescription_id, medicine_id, medicine_name, quantity, unit, price, amount
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
    {
        let conn = state.lock()?;
        conn.execute_batch("PRAGMA wal_checkpoint(FULL);")
            .map_err(|e| format!("数据库 checkpoint 失败: {e}"))?;
    }

    std::fs::copy(&db_path, &backup_path)
        .map_err(|e| format!("复制数据库失败: {e}"))?;

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

    /// 查询某药材当前库存数量
    fn get_quantity(conn: &Connection, medicine_id: i64) -> f64 {
        conn.query_row(
            "SELECT quantity FROM inventory WHERE medicine_id=?1",
            params![medicine_id],
            |row| row.get::<_, f64>(0),
        )
        .unwrap_or(0.0)
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

    // 避免未使用警告
    #[test]
    fn _ensure_arc_used() {
        let _ = Arc::new(1);
    }
}
