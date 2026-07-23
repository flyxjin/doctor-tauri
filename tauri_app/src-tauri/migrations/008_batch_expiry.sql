-- =====================================================================
-- 008_batch_expiry.sql
-- 中药材销售管理系统 - 批次+效期管理改造
-- 用途：将 inventory 表从"一药一行"改为"一批次一行"，支持多批次、效期管理
-- 策略：重建表（SQLite 无法直接 DROP UNIQUE 约束）+ 数据迁移 + 关联表加字段
-- 生成时间：2026-07-23
-- 向后兼容：存量库存记录转为 batch_no='初始库存'，效期为 NULL
-- =====================================================================

-- ====================
-- 1. 重建 inventory 表（移除 medicine_id UNIQUE，新增批次字段）
-- ====================

-- 1.1 重命名旧表
ALTER TABLE inventory RENAME TO inventory_old;

-- 1.2 创建新表（移除 medicine_id UNIQUE，新增批次字段）
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id INTEGER NOT NULL,
    batch_no TEXT NOT NULL DEFAULT '',
    production_date TEXT,
    expiry_date TEXT,
    quantity REAL NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT 'g',
    price REAL NOT NULL DEFAULT 0,
    min_stock REAL NOT NULL DEFAULT 0,
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
);

-- 1.3 迁移存量数据：转为"初始库存"批次，效期为 NULL
INSERT INTO inventory (medicine_id, batch_no, production_date, expiry_date,
                       quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT medicine_id, '初始库存', NULL, NULL,
       quantity, unit, price, min_stock, notes, created_at, updated_at
FROM inventory_old;

-- 1.4 创建索引
CREATE INDEX IF NOT EXISTS idx_inventory_medicine_id ON inventory (medicine_id);
CREATE INDEX IF NOT EXISTS idx_inventory_expiry_date ON inventory (expiry_date);
CREATE INDEX IF NOT EXISTS idx_inventory_batch_no ON inventory (batch_no);
-- 联合唯一约束：同一药材同一批次号不能重复
CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_medicine_batch ON inventory (medicine_id, batch_no);

-- 1.5 删除旧表
DROP TABLE inventory_old;

-- ====================
-- 2. prescription_items 增加批次关联（记录扣减的批次，删除处方时精确回扣）
-- ====================
ALTER TABLE prescription_items ADD COLUMN batch_id INTEGER;

-- ====================
-- 3. inventory_history 增加批次关联（按批次追溯）
-- ====================
ALTER TABLE inventory_history ADD COLUMN batch_id INTEGER;
