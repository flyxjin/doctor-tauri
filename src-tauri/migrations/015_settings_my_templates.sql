-- 015: 应用设置 + 我的方剂
--
-- app_settings：键值对应用设置（诊所抬头等），供打印处方笺等场景读取。
-- my_templates：医生个人习惯方（"另存为我的方剂"），items 为 JSON 数组
--   （[{name, quantity, unit}]，药材名对应 medicines.name）。

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS my_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    indication TEXT DEFAULT '',
    items TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
