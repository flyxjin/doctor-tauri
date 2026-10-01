// 数据备份核心逻辑：供 create_backup 命令与启动时自动每日备份共用
//
// 自动备份策略：
// - 每日首次启动时，若当天尚无任何备份（手动或自动），静默创建一份
//   `medicine_system_auto_YYYYMMDD_HHMMSS.db`；
// - 仅自动备份参与保留策略（默认保留最近 14 份），手动备份永不清理。

use crate::commands::compute_file_sha256;
use crate::models::BackupInfo;
use rusqlite::Connection;
use std::path::Path;

/// 自动备份保留份数（超出后删除最旧的自动备份）
pub const AUTO_BACKUP_KEEP: usize = 14;

/// 创建数据库备份文件：checkpoint 落盘 → 复制 → SHA256 → 写清单
///
/// `filename_stem` 为不含扩展名的文件名（如 `medicine_system_20260927_120000`
/// 或 `medicine_system_auto_20260927_120000`），生成 `<stem>.db` 与 `<stem>.json`。
pub fn create_backup_file(
    conn: &Connection,
    app_data_dir: &Path,
    filename_stem: &str,
) -> Result<BackupInfo, String> {
    let db_path = app_data_dir.join("medicine_system.db");
    if !db_path.exists() {
        return Err(format!("数据库文件不存在: {}", db_path.display()));
    }
    let backup_dir = app_data_dir.join("backups");
    std::fs::create_dir_all(&backup_dir).map_err(|e| format!("创建备份目录失败: {e}"))?;

    let now = chrono::Local::now();
    let timestamp = now.format("%Y%m%d_%H%M%S").to_string();
    let created_at = now.format("%Y-%m-%d %H:%M:%S").to_string();
    let backup_filename = format!("{filename_stem}.db");
    let backup_path = backup_dir.join(&backup_filename);

    // WAL 数据先落盘；调用方持有连接锁时完成 checkpoint + 复制，防止并发写入不一致
    conn.execute_batch("PRAGMA wal_checkpoint(FULL);")
        .map_err(|e| format!("数据库 checkpoint 失败: {e}"))?;
    std::fs::copy(&db_path, &backup_path).map_err(|e| format!("复制数据库失败: {e}"))?;

    let file_size = std::fs::metadata(&backup_path)
        .map(|m| m.len())
        .unwrap_or(0);
    let checksum = compute_file_sha256(&backup_path)?;

    let manifest = serde_json::json!({
        "backup_path": backup_path.to_string_lossy(),
        "file_size": file_size,
        "checksum": checksum,
        "created_at": created_at,
        "timestamp": timestamp,
        "filename": backup_filename,
    });
    let manifest_path = backup_dir.join(format!("{filename_stem}.json"));
    std::fs::write(
        &manifest_path,
        serde_json::to_string_pretty(&manifest).map_err(|e| format!("序列化清单失败: {e}"))?,
    )
    .map_err(|e| format!("写入清单失败: {e}"))?;

    Ok(BackupInfo {
        backup_path: backup_path.to_string_lossy().to_string(),
        file_size,
        checksum,
        created_at,
    })
}

/// 当天是否已有备份：手动（`medicine_system_YYYYMMDD_*`）或自动
/// （`medicine_system_auto_YYYYMMDD_*`）任一存在即视为已备份
pub fn has_backup_today(backup_dir: &Path, today: &str) -> bool {
    let marker = format!("_{today}");
    let Ok(entries) = std::fs::read_dir(backup_dir) else {
        return false;
    };
    entries.flatten().any(|e| {
        let name = e.file_name();
        let name = name.to_string_lossy();
        name.starts_with("medicine_system_") && name.contains(&marker) && name.ends_with(".db")
    })
}

/// 启动时自动备份入口：当天尚无备份则静默创建一份并按保留策略清理旧自动备份。
/// 任何失败仅输出 stderr，绝不阻塞应用启动。
pub fn auto_backup_if_needed(app_data_dir: &Path, conn: &Connection) {
    let result = (|| -> Result<(), String> {
        let backup_dir = app_data_dir.join("backups");
        let today = chrono::Local::now().format("%Y%m%d").to_string();
        if has_backup_today(&backup_dir, &today) {
            return Ok(());
        }
        let stem = format!(
            "medicine_system_auto_{}",
            chrono::Local::now().format("%Y%m%d_%H%M%S")
        );
        let info = create_backup_file(conn, app_data_dir, &stem)?;
        let removed = prune_auto_backups(&backup_dir, AUTO_BACKUP_KEEP)?;
        println!(
            "[backup] 已自动创建每日备份 {}（清理过期自动备份 {removed} 份）",
            info.backup_path
        );
        Ok(())
    })();
    if let Err(e) = result {
        eprintln!("[backup] 自动备份失败（不影响启动）: {e}");
    }
}

/// 清理最旧的自动备份（`medicine_system_auto_*`），保留最近 `keep` 份；
/// 手动备份不受影响。返回删除的份数。
pub fn prune_auto_backups(backup_dir: &Path, keep: usize) -> Result<usize, String> {
    let mut autos: Vec<std::path::PathBuf> = match std::fs::read_dir(backup_dir) {
        Ok(entries) => entries
            .flatten()
            .map(|e| e.path())
            .filter(|p| {
                p.file_name()
                    .and_then(|n| n.to_str())
                    .map(|n| n.starts_with("medicine_system_auto_") && n.ends_with(".db"))
                    .unwrap_or(false)
            })
            .collect(),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(0),
        Err(e) => return Err(format!("读取备份目录失败: {e}")),
    };
    // 文件名内嵌时间戳，按名称排序即按时间排序
    autos.sort();
    if autos.len() <= keep {
        return Ok(0);
    }
    let to_remove = autos.len() - keep;
    for path in &autos[..to_remove] {
        std::fs::remove_file(path)
            .map_err(|e| format!("清理旧备份失败 ({}): {e}", path.display()))?;
        let manifest = path.with_extension("json");
        if manifest.exists() {
            let _ = std::fs::remove_file(manifest);
        }
    }
    Ok(to_remove)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn temp_dir(tag: &str) -> std::path::PathBuf {
        let dir = std::env::temp_dir().join(format!(
            "backup_test_{}_{}_{tag}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir_all(&dir).unwrap();
        dir
    }

    #[test]
    fn test_create_backup_file_roundtrip() {
        let dir = temp_dir("roundtrip");
        let db_path = dir.join("medicine_system.db");
        let conn = Connection::open(&db_path).unwrap();
        conn.execute_batch("CREATE TABLE t(v TEXT); INSERT INTO t VALUES('药');")
            .unwrap();

        let info =
            create_backup_file(&conn, &dir, "medicine_system_20260927_120000").expect("备份应成功");
        let backup_path = std::path::PathBuf::from(&info.backup_path);
        assert!(backup_path.exists(), "备份文件应存在");
        assert!(backup_path.with_extension("json").exists(), "清单应存在");
        assert_eq!(
            info.checksum,
            compute_file_sha256(&backup_path).expect("重新计算校验和应成功"),
            "清单校验和应与文件一致"
        );

        // 备份副本应可独立打开并查询（验证复制完整性）
        {
            let copied = Connection::open(&backup_path).unwrap();
            let v: String = copied
                .query_row("SELECT v FROM t LIMIT 1", [], |r| r.get(0))
                .unwrap();
            assert_eq!(v, "药");
        } // copied 在此 drop，释放文件句柄后再清理临时目录

        drop(conn); // 释放主库句柄（Windows 下先关句柄再删目录）
        std::fs::remove_dir_all(&dir).unwrap();
    }

    #[test]
    fn test_has_backup_today() {
        let dir = temp_dir("today");
        let today = "20260927";
        assert!(!has_backup_today(&dir, today), "空目录应视为无备份");

        std::fs::write(dir.join("medicine_system_20260926_100000.db"), b"x").unwrap();
        assert!(!has_backup_today(&dir, today), "仅昨日备份不算今日已备份");

        std::fs::write(dir.join("medicine_system_20260927_120000.db"), b"x").unwrap();
        assert!(has_backup_today(&dir, today), "今日手动备份应命中");

        std::fs::write(dir.join("medicine_system_auto_20260927_130000.db"), b"x").unwrap();
        assert!(has_backup_today(&dir, today), "今日自动备份应命中");

        std::fs::remove_dir_all(&dir).unwrap();
    }

    #[test]
    fn test_prune_auto_backups_keeps_manual() {
        let dir = temp_dir("prune");
        // 5 份自动备份 + 2 份手动备份
        for d in ["20260921", "20260922", "20260923", "20260924", "20260925"] {
            std::fs::write(
                dir.join(format!("medicine_system_auto_{d}_090000.db")),
                b"x",
            )
            .unwrap();
            std::fs::write(
                dir.join(format!("medicine_system_auto_{d}_090000.json")),
                b"{}",
            )
            .unwrap();
        }
        for d in ["20260920", "20260926"] {
            std::fs::write(dir.join(format!("medicine_system_{d}_100000.db")), b"x").unwrap();
        }

        let removed = prune_auto_backups(&dir, 3).unwrap();
        assert_eq!(removed, 2, "5 份保留 3 份应删除最旧 2 份");
        assert!(!dir.join("medicine_system_auto_20260921_090000.db").exists());
        assert!(!dir.join("medicine_system_auto_20260922_090000.db").exists());
        assert!(dir.join("medicine_system_auto_20260923_090000.db").exists());
        assert!(
            !dir.join("medicine_system_auto_20260921_090000.json")
                .exists(),
            "被删备份的清单应一并删除"
        );
        // 手动备份不受保留策略影响
        assert!(dir.join("medicine_system_20260920_100000.db").exists());
        assert!(dir.join("medicine_system_20260926_100000.db").exists());

        // 已不超限时再次调用应无动作
        assert_eq!(prune_auto_backups(&dir, 3).unwrap(), 0);
        std::fs::remove_dir_all(&dir).unwrap();
    }
}
