-- =====================================================================
-- 001_init.sql
-- 中药材销售管理系统 - 初始 schema 与示例数据
-- 表结构与原 Python 项目（d:\learn\trae\python_app）完全兼容，可共享数据
-- =====================================================================

-- 药材表
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    alias TEXT DEFAULT '',
    category TEXT DEFAULT '',
    nature TEXT DEFAULT '',
    taste TEXT DEFAULT '',
    meridian TEXT DEFAULT '',
    efficacy TEXT DEFAULT '',
    indications TEXT DEFAULT '',
    usage TEXT DEFAULT '',
    dosage TEXT DEFAULT '',
    contraindication TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 库存表
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id INTEGER NOT NULL UNIQUE,
    quantity REAL NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT 'g',
    price REAL NOT NULL DEFAULT 0,
    min_stock REAL NOT NULL DEFAULT 0,
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
);

-- 处方表
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT DEFAULT '',
    patient_age INTEGER,
    patient_gender TEXT DEFAULT '',
    diagnosis TEXT DEFAULT '',
    total_amount REAL DEFAULT 0,
    created_by TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 处方明细表
CREATE TABLE IF NOT EXISTS prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    medicine_name TEXT NOT NULL,
    quantity REAL NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT 'g',
    price REAL NOT NULL DEFAULT 0,
    amount REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);

-- 库存变更历史表
CREATE TABLE IF NOT EXISTS inventory_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id INTEGER NOT NULL,
    medicine_name TEXT NOT NULL,
    type TEXT NOT NULL,
    quantity REAL NOT NULL DEFAULT 0,
    price REAL,
    total_amount REAL,
    operator TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    operator TEXT DEFAULT '',
    details TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 数据版本表（内置数据装载版本追踪）
CREATE TABLE IF NOT EXISTS data_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    medicine_count INTEGER NOT NULL,
    checksum TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- 索引
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines (name);
CREATE INDEX IF NOT EXISTS idx_medicines_category ON medicines (category);
CREATE INDEX IF NOT EXISTS idx_inventory_medicine_id ON inventory (medicine_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_created_at ON prescriptions (created_at);
CREATE INDEX IF NOT EXISTS idx_inventory_history_medicine_id ON inventory_history (medicine_id);
CREATE INDEX IF NOT EXISTS idx_prescription_items_prescription_id ON prescription_items (prescription_id);
CREATE INDEX IF NOT EXISTS idx_prescription_items_medicine_id ON prescription_items (medicine_id);
CREATE INDEX IF NOT EXISTS idx_operation_logs_target_type ON operation_logs (target_type);
CREATE INDEX IF NOT EXISTS idx_inventory_history_created_at ON inventory_history (created_at);

-- =====================================================================
-- 示例数据：5 味常用中药材（内置 300 味数据的完整迁移见后续迁移脚本）
-- =====================================================================
INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes) VALUES
('人参', '棒槌、园参', '补虚药', '微温', '甘、微苦', '脾、肺、心经',
 '大补元气，复脉固脱，补脾益肺，生津养血，安神增智',
 '体虚欲脱，肢冷脉微，脾虚食少，肺虚喘咳，津伤口渴，内热消渴，气血亏虚，久病虚羸，惊悸失眠',
 '煎服，另煎兑服', '3-9g，挽救脱证可用至15-30g',
 '实证、热证而正气不虚者忌服', '不宜与藜芦同用'),
('黄芪', '绵黄芪、黄耆', '补虚药', '微温', '甘', '脾、肺经',
 '补气升阳，固表止汗，利水消肿，生津养血，行滞通痹，托毒排脓，敛疮生肌',
 '气虚乏力，食少便溏，中气下陷，久泻脱肛，便血崩漏，表虚自汗，气虚水肿，内热消渴',
 '煎服', '9-30g',
 '凡表实邪盛、阴虚阳亢者均须忌服', '蜜炙可增强补中益气作用'),
('当归', '秦归、云归', '补虚药', '温', '甘、辛', '肝、心、脾经',
 '补血活血，调经止痛，润肠通便',
 '血虚萎黄，眩晕心悸，月经不调，经闭痛经，虚寒腹痛，风湿痹痛，跌扑损伤，痈疽疮疡，肠燥便秘',
 '煎服', '6-12g',
 '湿盛中满、大便溏泄者忌服', '酒当归活血通经，用于经闭痛经、风湿痹痛'),
('白术', '于术、冬术', '补虚药', '温', '苦、甘', '脾、胃经',
 '健脾益气，燥湿利水，止汗，安胎',
 '脾虚食少，腹胀泄泻，痰饮眩悸，水肿，自汗，胎动不安',
 '煎服', '6-12g',
 '阴虚燥渴、气滞胀闷者忌服', '麸炒白术健脾作用增强'),
('甘草', '甜根子、甜草', '补虚药', '平', '甘', '心、肺、脾、胃经',
 '补脾益气，清热解毒，祛痰止咳，缓急止痛，调和诸药',
 '脾胃虚弱，倦怠乏力，心悸气短，咳嗽痰多，脘腹四肢挛急疼痛，痈肿疮毒',
 '煎服', '2-10g',
 '不宜与甘遂、大戟、海藻、芫花同用', '十八反：甘草反甘遂、大戟、海藻、芫花');

-- 为示例药材创建库存记录
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock) VALUES
((SELECT id FROM medicines WHERE name='人参'), 500, 'g', 0.8, 100),
((SELECT id FROM medicines WHERE name='黄芪'), 2000, 'g', 0.15, 300),
((SELECT id FROM medicines WHERE name='当归'), 1500, 'g', 0.2, 200),
((SELECT id FROM medicines WHERE name='白术'), 800, 'g', 0.18, 150),
((SELECT id FROM medicines WHERE name='甘草'), 3000, 'g', 0.1, 500);

-- 记录数据版本
INSERT OR IGNORE INTO data_version (version, medicine_count, checksum) VALUES ('1.0.0', 5, NULL);
