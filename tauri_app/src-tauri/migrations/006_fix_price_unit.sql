-- =====================================================================
-- 006_fix_price_unit.sql
-- 中药材销售管理系统 - 修复价格单位（元/100g → 元/g）
-- 用途：005_redesign_prices.sql 将 inventory.price 设为"元/100g"语义，
--       但系统所有金额计算公式为 quantity(g) × price，按"元/g"计算，
--       导致所有金额被放大 100 倍。本迁移将所有 price 相关字段统一除以 100，
--       转换为"元/g"语义，使现有计算公式 quantity × price 自动正确。
-- 生成时间：2026-07-22
-- 影响表：inventory / prescription_items / inventory_history / prescriptions
-- 安全性：所有 UPDATE 使用数学除法，无数据丢失风险；
--         inventory_history.price/total_amount 可为 NULL，使用 NULLIF 安全处理。
-- =====================================================================

-- 1. 修正库存表单价（元/100g → 元/g）
UPDATE inventory SET price = price / 100.0;

-- 2. 修正处方明细的单价和金额快照
UPDATE prescription_items SET
    price = price / 100.0,
    amount = amount / 100.0;

-- 3. 修正库存变更历史的单价和金额快照（price/total_amount 可为 NULL）
UPDATE inventory_history SET
    price = CASE WHEN price IS NOT NULL THEN price / 100.0 ELSE NULL END,
    total_amount = CASE WHEN total_amount IS NOT NULL THEN total_amount / 100.0 ELSE NULL END;

-- 4. 修正处方总金额
UPDATE prescriptions SET total_amount = total_amount / 100.0;
