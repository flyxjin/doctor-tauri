-- =====================================================================
-- 009_prescription_item_batches.sql
-- 处方明细-批次扣减关联表
--
-- 背景：008 批次改造后，create_prescription 跨多批次扣减库存时，
-- prescription_items.batch_id 只记录首个批次，删除处方时整量回扣到
-- 该批次，导致其他被扣批次永久失库存（数据正确性 bug）。
--
-- 本迁移新建关联表，记录每个处方明细的实际批次扣减明细，
-- 删除处方时按明细精确回扣到各批次。
-- =====================================================================

CREATE TABLE IF NOT EXISTS prescription_item_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_item_id INTEGER NOT NULL,
    batch_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    price REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (prescription_item_id) REFERENCES prescription_items(id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES inventory(id)
);

CREATE INDEX IF NOT EXISTS idx_pib_item_id ON prescription_item_batches (prescription_item_id);
CREATE INDEX IF NOT EXISTS idx_pib_batch_id ON prescription_item_batches (batch_id);
