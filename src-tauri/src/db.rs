// SQLite 连接管理：单例连接由 Tauri State 管理，通过 Mutex 保护并发访问

use rusqlite::{Connection, OptionalExtension};
use std::path::Path;
use std::sync::{Mutex, MutexGuard};

/// 编译期嵌入所有迁移文件：按文件名升序排列，运行时依次执行。
///
/// 由于 Tauri 应用打包后源码目录不一定存在，这里通过 `include_str!` 把
/// `migrations/` 目录下所有 .sql 文件嵌入二进制，等价于"遍历目录"。
/// 新增迁移时只需在此数组末尾追加一项，并保持文件名升序。
///
/// 元组含义：(version, sql)，其中 version = 文件名去除 .sql 后缀
const MIGRATIONS: &[(&str, &str)] = &[
    ("001_init", include_str!("../migrations/001_init.sql")),
    (
        "002_seed_medicines",
        include_str!("../migrations/002_seed_medicines.sql"),
    ),
    ("003_patients", include_str!("../migrations/003_patients.sql")),
    (
        "004_supplement_herbs",
        include_str!("../migrations/004_supplement_herbs.sql"),
    ),
    (
        "005_redesign_prices",
        include_str!("../migrations/005_redesign_prices.sql"),
    ),
];

/// 数据库状态：持有单个 SQLite 连接，通过 Mutex 序列化访问
pub struct DbState {
    conn: Mutex<Connection>,
}

impl DbState {
    /// 打开（或创建）指定路径的数据库文件，并启用外键约束。
    ///
    /// 传入 `Path::new(":memory:")` 可创建内存数据库（用于单元测试）。
    pub fn new(path: &Path) -> Result<Self, String> {
        let conn = Connection::open(path).map_err(|e| format!("打开数据库失败: {e}"))?;
        conn.execute_batch("PRAGMA foreign_keys = ON;")
            .map_err(|e| format!("设置数据库 PRAGMA 失败: {e}"))?;
        Ok(Self {
            conn: Mutex::new(conn),
        })
    }

    /// 执行所有尚未应用的迁移文件。
    ///
    /// 实现策略：
    /// 1. 创建 `schema_migrations` 表（若不存在）记录已应用的迁移版本
    /// 2. 遍历编译期嵌入的 `MIGRATIONS` 数组（按文件名升序）
    /// 3. 对每个文件，若 `schema_migrations` 中已存在该 version 则跳过
    /// 4. 否则在事务内执行 SQL 并写入 `schema_migrations`
    ///
    /// 该方法幂等：多次调用不会重复执行已应用的迁移。
    pub fn run_migrations(&self) -> Result<(), String> {
        let conn = self.lock()?;
        // 创建迁移追踪表（version = 文件名去除 .sql 后缀）
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            );",
        )
        .map_err(|e| format!("创建 schema_migrations 表失败: {e}"))?;

        for (version, sql) in MIGRATIONS {
            // 检查是否已应用
            let already: Option<i64> = conn
                .query_row(
                    "SELECT 1 FROM schema_migrations WHERE version = ?1",
                    rusqlite::params![version],
                    |row| row.get(0),
                )
                .optional()
                .map_err(|e| format!("查询迁移状态失败: {e}"))?;
            if already.is_some() {
                continue;
            }

            // 在事务内执行迁移 + 记录，确保原子性
            let tx = conn
                .unchecked_transaction()
                .map_err(|e| format!("开启事务失败: {e}"))?;
            tx.execute_batch(sql)
                .map_err(|e| format!("执行迁移 {version} 失败: {e}"))?;
            tx.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?1, datetime('now'))",
                rusqlite::params![version],
            )
            .map_err(|e| format!("记录迁移 {version} 状态失败: {e}"))?;
            tx.commit()
                .map_err(|e| format!("提交迁移 {version} 事务失败: {e}"))?;
        }
        Ok(())
    }

    /// 获取连接的互斥锁守卫，供 commands 串行执行 SQL
    pub fn lock(&self) -> Result<MutexGuard<'_, Connection>, String> {
        self.conn.lock().map_err(|e| format!("获取数据库锁失败: {e}"))
    }
}

// ==================== 单元测试 ====================

#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::params;

    /// 辅助函数：打开内存数据库并执行所有迁移
    fn setup_in_memory() -> DbState {
        let db = DbState::new(Path::new(":memory:")).expect("打开内存数据库失败");
        db.run_migrations().expect("执行迁移失败");
        db
    }

    /// 测试 run_migrations 创建所有 7 张业务表 + schema_migrations 追踪表
    #[test]
    fn test_run_migrations_creates_all_tables() {
        let db = setup_in_memory();
        let conn = db.lock().unwrap();
        let tables: Vec<String> = conn
            .prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            .unwrap()
            .query_map((), |row| row.get::<_, String>(0))
            .unwrap()
            .map(|r| r.unwrap())
            .collect();
        // 7 张业务表
        for expected in [
            "medicines",
            "inventory",
            "prescriptions",
            "prescription_items",
            "inventory_history",
            "operation_logs",
            "data_version",
        ] {
            assert!(
                tables.contains(&expected.to_string()),
                "缺少表: {expected}, 实际表: {tables:?}"
            );
        }
        // 迁移追踪表
        assert!(tables.contains(&"schema_migrations".to_string()));
        // 业务表数量至少 7 张
        let business_tables: Vec<_> = tables
            .iter()
            .filter(|t| !t.starts_with("sqlite_") && t.as_str() != "schema_migrations")
            .collect();
        assert!(
            business_tables.len() >= 7,
            "业务表数量不足 7 张: {business_tables:?}"
        );
    }

    /// 测试 schema_migrations 表正确记录了已应用的迁移版本
    #[test]
    fn test_schema_migrations_records_applied() {
        let db = setup_in_memory();
        let conn = db.lock().unwrap();
        let applied: Vec<String> = conn
            .prepare("SELECT version FROM schema_migrations ORDER BY version")
            .unwrap()
            .query_map((), |row| row.get::<_, String>(0))
            .unwrap()
            .map(|r| r.unwrap())
            .collect();
        assert_eq!(applied.len(), MIGRATIONS.len());
        for (version, _) in MIGRATIONS {
            assert!(applied.contains(&version.to_string()));
        }
    }

    /// 测试 run_migrations 幂等：多次调用不会重复执行迁移
    #[test]
    fn test_run_migrations_idempotent() {
        let db = setup_in_memory();
        // 再次调用不应报错，也不应重复应用迁移
        db.run_migrations().expect("重复执行迁移应成功");
        let conn = db.lock().unwrap();
        // schema_migrations 中记录数应等于 MIGRATIONS 长度，不重复
        let count: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM schema_migrations",
                (),
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(count as usize, MIGRATIONS.len());
    }

    /// 测试插入药材 + 查询能正确往返
    #[test]
    fn test_insert_and_query_medicine_roundtrip() {
        let db = setup_in_memory();
        let conn = db.lock().unwrap();
        // 插入一味新药材（避免与种子数据冲突）
        conn.execute(
            "INSERT INTO medicines (name, alias, category, nature, taste) VALUES (?1, ?2, ?3, ?4, ?5)",
            params!["测试药材A", "测试别名A", "补虚药", "温", "甘"],
        )
        .unwrap();
        let id = conn.last_insert_rowid();
        // 查询回来验证
        let (name, alias, category, nature, taste): (String, String, String, String, String) = conn
            .query_row(
                "SELECT name, alias, category, nature, taste FROM medicines WHERE id = ?1",
                params![id],
                |row| {
                    Ok((
                        row.get(0)?,
                        row.get(1)?,
                        row.get(2)?,
                        row.get(3)?,
                        row.get(4)?,
                    ))
                },
            )
            .unwrap();
        assert_eq!(name, "测试药材A");
        assert_eq!(alias, "测试别名A");
        assert_eq!(category, "补虚药");
        assert_eq!(nature, "温");
        assert_eq!(taste, "甘");
    }

    /// 测试插入库存并验证外键关联
    #[test]
    fn test_insert_inventory_with_foreign_key() {
        let db = setup_in_memory();
        let conn = db.lock().unwrap();
        // 插入药材
        conn.execute(
            "INSERT INTO medicines (name) VALUES ('fk_test_medicine')",
            params![],
        )
        .unwrap();
        let medicine_id = conn.last_insert_rowid();
        // 插入库存
        conn.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 200, 'g', 50.5, 30)",
            params![medicine_id],
        )
        .unwrap();
        // 联表查询
        let (mname, qty, price): (String, f64, f64) = conn
            .query_row(
                "SELECT m.name, i.quantity, i.price FROM inventory i \
                 JOIN medicines m ON i.medicine_id = m.id \
                 WHERE i.medicine_id = ?1",
                params![medicine_id],
                |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)),
            )
            .unwrap();
        assert_eq!(mname, "fk_test_medicine");
        assert_eq!(qty, 200.0);
        assert_eq!(price, 50.5);
    }

    /// 测试外键 CASCADE 删除：删除药材后 inventory 自动删除
    #[test]
    fn test_foreign_key_cascade_delete() {
        let db = setup_in_memory();
        let conn = db.lock().unwrap();
        // 插入药材 + 库存
        conn.execute(
            "INSERT INTO medicines (name) VALUES ('cascade_test_medicine')",
            params![],
        )
        .unwrap();
        let medicine_id = conn.last_insert_rowid();
        conn.execute(
            "INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES (?1, 100, 'g', 50, 10)",
            params![medicine_id],
        )
        .unwrap();
        // 确认库存存在
        let count_before: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM inventory WHERE medicine_id = ?1",
                params![medicine_id],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(count_before, 1);
        // 删除药材，触发级联删除
        conn.execute(
            "DELETE FROM medicines WHERE id = ?1",
            params![medicine_id],
        )
        .unwrap();
        // 库存应被级联删除
        let count_after: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM inventory WHERE medicine_id = ?1",
                params![medicine_id],
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(count_after, 0, "删除药材后库存应被级联删除");
    }

    /// 测试种子数据已被迁移脚本插入：300 味种子药材 + 19 味补充药材 = 319 味
    #[test]
    fn test_seed_data_inserted() {
        let db = setup_in_memory();
        let conn = db.lock().unwrap();
        // 002_seed_medicines.sql 插入 300 味药材，加上 001_init.sql 已有 5 味（重名被 IGNORE）
        // 004_supplement_herbs.sql 再补充 19 味方剂模板引用药材
        // 所以最终 medicines 表应有 319 条
        let medicine_count: i64 = conn
            .query_row("SELECT COUNT(*) FROM medicines", (), |row| row.get(0))
            .unwrap();
        assert_eq!(medicine_count, 319, "种子+补充应共 319 味药材");
        // 库存记录应至少 319 条（每味药材对应一条库存）
        let inventory_count: i64 = conn
            .query_row("SELECT COUNT(*) FROM inventory", (), |row| row.get(0))
            .unwrap();
        assert!(
            inventory_count >= 319,
            "库存记录至少 319 条，实际: {inventory_count}"
        );
        // 验证特定药材存在
        let exists: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM medicines WHERE name = '人参'",
                (),
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(exists, 1);
        let exists: i64 = conn
            .query_row(
                "SELECT COUNT(*) FROM medicines WHERE name = '水蛭'",
                (),
                |row| row.get(0),
            )
            .unwrap();
        assert_eq!(exists, 1);
    }

    /// 测试 DbState::new 在 :memory: 路径下能正常工作
    #[test]
    fn test_db_state_new_with_memory_path() {
        let db = DbState::new(Path::new(":memory:")).expect("打开 :memory: 数据库失败");
        // 验证连接可用
        let conn = db.lock().unwrap();
        let _: i64 = conn
            .query_row("SELECT 1", (), |row| row.get(0))
            .expect("基础查询应成功");
        // 外键约束应已启用
        let fk: i64 = conn
            .query_row("PRAGMA foreign_keys", (), |row| row.get(0))
            .unwrap();
        assert_eq!(fk, 1, "外键约束应已启用");
    }
}
