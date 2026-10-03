-- 012: 处方关联患者档案（外键）
--
-- 背景：此前 prescriptions 仅按 patient_name 与 patients 弱关联，客户改名后
-- 历史处方归档与患者统计随之漂移。新增可空 patient_id 外键建立强关联。
--
-- 回填策略：历史处方按姓名「唯一匹配」患者档案时补 patient_id；
-- 重名或无档案的历史处方保持 NULL，继续按姓名关联，避免错误归档。
-- 新处方由 create_prescription 在姓名唯一匹配时写入 patient_id（服务端校验存在性）。

ALTER TABLE prescriptions ADD COLUMN patient_id INTEGER REFERENCES patients(id);

UPDATE prescriptions
SET patient_id = (
    SELECT p.id FROM patients p WHERE p.name = prescriptions.patient_name
)
WHERE patient_id IS NULL
  AND prescriptions.patient_name <> ''
  AND (SELECT COUNT(*) FROM patients p2 WHERE p2.name = prescriptions.patient_name) = 1;
