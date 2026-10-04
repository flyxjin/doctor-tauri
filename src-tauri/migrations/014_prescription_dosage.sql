-- 014: 处方帖数与煎服法
--
-- 背景：真实开方以"帖"为单位（如七剂，每日一剂，分两次温服），此前 prescriptions
-- 只有单帖明细与单帖总额，缺少 dosage_count（帖数）与 usage_method（煎服法），
-- 导致：收费需人工乘帖数、打印处方笺无用法、库存按单帖扣减。
--
-- 语义约定：
-- - prescription_items.quantity 为单帖用量（处方学惯例，打印/复用均按单帖展示）；
-- - 库存出库/回扣按 单帖用量 × 帖数 计算（create_prescription / 回扣明细均已存总量）；
-- - total_amount = Σ(明细单价×数量) × 帖数；
-- - 历史数据回填 dosage_count=1、usage_method=''，与旧口径（单帖）完全兼容。

ALTER TABLE prescriptions ADD COLUMN dosage_count INTEGER NOT NULL DEFAULT 1;
ALTER TABLE prescriptions ADD COLUMN usage_method TEXT DEFAULT '';

UPDATE prescriptions SET dosage_count = 1 WHERE dosage_count IS NULL OR dosage_count < 1;
