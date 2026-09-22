-- 010: 高频查询索引补齐
--
-- 患者历史/患者统计/删除患者引用检查均按 patient_name 精确匹配 prescriptions，
-- 无索引时随处方量增长退化为全表扫描。姓名关联是既有的弱关联设计（001 迁移），
-- 本迁移仅补索引不改变数据模型。
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_name
    ON prescriptions(patient_name);
