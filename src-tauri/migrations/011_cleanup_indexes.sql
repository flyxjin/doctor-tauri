-- 011: 索引补齐与遗留死表清理
--
-- 1. operation_logs 此前仅索引 target_type：设置页按操作类型筛选日志、
--    按日期范围查询（半开区间 created_at 比较）都会全表扫描。
--    日志表随时间无限增长，补索引避免逐渐变慢。
-- 2. data_version 表在 001 迁移创建后仅写入一条种子行，运行时代码从不读写
--    （数据/schema 版本实际由 schema_migrations 表追踪），属遗留死表，予以清理。
CREATE INDEX IF NOT EXISTS idx_operation_logs_operation_type ON operation_logs (operation_type);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON operation_logs (created_at);

DROP TABLE IF EXISTS data_version;
