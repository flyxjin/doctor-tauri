-- =====================================================================
-- 013_expand_herbs_clinical.sql
-- 中药材销售管理系统 - 补充临床常用药材（88 味）
-- 用途：在 002(300味) + 004(19味) + 007(81味) 共 400 味基础上，
--       补齐《中药学》教材范围内的临床常用药缺口，使总数达到 488 味。
--       重点补入：三七、五味子、石菖蒲、蜈蚣/全蝎/僵蚕/地龙、麝香/苏合香、
--       茵陈/金钱草/萆薢/猪苓、决明子、三棱/莪术、止血类（大蓟/小蓟/地榆/
--       槐花/侧柏叶/白茅根/茜草/蒲黄）、收涩类（乌梅/芡实/金樱子/桑螵蛸/
--       海螵蛸/覆盆子）、常用炮制品（炮姜/橘红/化橘红/鹿角胶）等。
-- 数据来源：《中药学》教材 + 《中国药典》
-- 生成时间：2026-10-03
-- 价格单位：元/g（与 006_fix_price_unit.sql 修复后基准一致）
-- 库存初始化：quantity=1000, unit='g', min_stock=100
-- 时间戳：created_at/updated_at 统一使用 '2026-07-17 00:00:00'
-- 使用 INSERT OR IGNORE 避免与已有数据冲突
-- 每味药材对应 2 条 SQL：medicines INSERT + inventory INSERT...SELECT
-- =====================================================================

-- ======================== 解表药（1 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('西河柳', '柽柳、山川柳、三春柳', '解表药', '平', '甘、辛', '归心、肺、胃经', '发表透疹，祛风除湿', '麻疹不透,风疹瘙痒,风湿痹痛', '煎服', '3-9g', '麻疹已透者不宜使用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '西河柳';

-- ======================== 清热药（15 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('寒水石', '凝水石、白水石', '清热药', '大寒', '辛、咸', '归心、胃、肾经', '清热泻火，利窍，消肿', '热病烦渴,癫狂,口舌生疮,热毒疮痈,丹毒烫伤', '煎服', '9-15g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.05, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '寒水石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('决明子', '草决明、马蹄决明', '清热药', '微寒', '甘、苦、咸', '归肝、大肠经', '清肝明目，润肠通便', '目赤涩痛,羞明多泪,头痛眩晕,目暗不明,大便秘结', '煎服', '9-15g', '气虚便溏者不宜用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.04, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '决明子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('谷精草', '谷精珠、戴星草', '清热药', '平', '辛、甘', '归肝、肺经', '疏散风热，明目退翳', '风热目赤,肿痛羞明,目生翳膜,风热头痛', '煎服', '9-15g', '阴虚血亏之眼疾慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '谷精草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('密蒙花', '蒙花、老蒙花', '清热药', '微寒', '甘', '归肝经', '清热泻火，养肝明目，退翳', '目赤肿痛,多泪羞明,目生翳膜,肝虚目暗,视物昏花', '煎服', '9-15g', '', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '密蒙花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('千里光', '千里及、九里明', '清热药', '寒', '苦', '归肺、肝、大肠经', '清热解毒，明目，利湿', '风热感冒,目赤肿痛,泄泻痢疾,皮肤湿疹,疮疖痈肿', '煎服', '15-30g', '不宜久服', '外用适量煎水洗', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.1, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '千里光';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('四季青', '冬青叶、红冬青', '清热药', '寒', '苦、涩', '归肺、大肠、膀胱经', '清热解毒，凉血止血，敛疮', '水火烫伤,湿疹,疮疡,下肢溃疡,外伤出血', '煎服', '15-30g', '脾胃虚寒者慎服', '外用适量', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.1, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '四季青';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('金荞麦', '野荞麦、开金锁', '清热药', '凉', '辛、苦', '归肺经', '清热解毒，排脓祛瘀', '肺痈吐脓,肺热喘咳,乳蛾肿痛,瘰疬疮疖', '煎服', '15-45g', '', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '金荞麦';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('大血藤', '红藤、活血藤', '清热药', '平', '苦', '归大肠、肝经', '清热解毒，活血，祛风止痛', '肠痈腹痛,热毒疮疡,经闭痛经,跌扑肿痛,风湿痹痛', '煎服', '9-15g', '孕妇慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '大血藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('重楼', '蚤休、七叶一枝花', '清热药', '微寒', '苦', '归肝经', '清热解毒，消肿止痛，凉肝定惊', '疔疮痈肿,咽喉肿痛,蛇虫咬伤,跌扑伤痛,惊风抽搐', '煎服', '3-9g', '体虚、无实火热毒者及孕妇忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.9, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '重楼';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('拳参', '草河车、紫参', '清热药', '微寒', '苦、涩', '归肺、肝、大肠经', '清热解毒，消肿，止血', '赤痢热泻,肺热咳嗽,痈肿瘰疬,口舌生疮,血热吐衄,痔疮出血', '煎服', '3-9g', '无实火热毒者不宜', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '拳参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('漏芦', '狼头花、野兰', '清热药', '寒', '苦', '归胃经', '清热解毒，消痈，下乳，舒筋通脉', '乳痈肿痛,痈疽发背,瘰疬疮毒,乳汁不通,湿痹拘挛', '煎服', '5-9g', '孕妇慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '漏芦';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('青果', '橄榄、青橄榄', '清热药', '平', '甘、酸', '归肺、胃经', '清热解毒，利咽，生津', '咽喉肿痛,咳嗽痰黏,烦热口渴,鱼蟹中毒', '煎服', '4.5-9g', '', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '青果';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('牛黄', '丑宝、心黄', '清热药', '凉', '甘', '归心、肝经', '清心，豁痰，开窍，凉肝，息风，解毒', '热病神昏,中风痰迷,惊痫抽搐,癫痫发狂,咽喉肿痛,口舌生疮,痈肿疔疮', '入丸散', '0.15-0.35g', '非实热证不宜用,孕妇慎用', '现多用人培植牛黄或人工牛黄', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 2.0, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '牛黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('皂角刺', '皂荚刺、皂刺', '清热药', '温', '辛', '归肝、胃经', '消肿托毒，排脓，杀虫', '痈疽初起或脓成不溃,外治疥癣麻风', '煎服', '3-9g', '痈疽已溃者不宜服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '皂角刺';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('天葵子', '紫背天葵、夏无踪', '清热药', '寒', '甘、苦', '归肝、胃经', '清热解毒，消肿散结', '痈肿疔疮,瘰疬,乳痈,毒蛇咬伤', '煎服', '9-15g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '天葵子';

-- ======================== 祛风湿药（2 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('徐长卿', '寮刁竹、逍遥竹', '祛风湿药', '温', '辛', '归肝、胃经', '祛风，化湿，止痛，止痒', '风湿痹痛,胃痛胀满,牙痛,腰痛,跌扑伤痛,风疹,湿疹瘙痒', '煎服', '3-12g', '体弱者慎服', '不宜久煎', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '徐长卿';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('路路通', '枫果、狼眼', '祛风湿药', '平', '苦', '归肝、肾经', '祛风活络，利水，通经', '关节痹痛,麻木拘挛,水肿胀满,乳少,经闭', '煎服', '5-9g', '孕妇慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.1, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '路路通';

-- ======================== 利水渗湿药（9 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('茵陈', '绵茵陈、茵陈蒿', '利水渗湿药', '微寒', '苦、辛', '归脾、胃、肝、胆经', '清利湿热，利胆退黄', '黄疸尿少,湿温暑湿,湿疮瘙痒', '煎服', '6-15g', '蓄血发黄及血虚萎黄者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '茵陈';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('金钱草', '过路黄、大金钱草', '利水渗湿药', '微寒', '甘、咸', '归肝、胆、肾、膀胱经', '利湿退黄，利尿通淋，解毒消肿', '湿热黄疸,胆胀胁痛,石淋,热淋,小便涩痛,痈肿疔疮,蛇虫咬伤', '煎服', '15-60g', '', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '金钱草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('萆薢', '粉萆薢、绵萆薢', '利水渗湿药', '平', '苦', '归肾、胃经', '利湿去浊，祛风除痹', '膏淋,白浊,白带过多,风湿痹痛,关节不利,腰膝疼痛', '煎服', '9-15g', '肾阴亏虚遗精滑精者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '萆薢';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('猪苓', '野猪苓、猪屎苓', '利水渗湿药', '平', '甘、淡', '归肾、膀胱经', '利水渗湿', '水肿,小便不利,泄泻,淋浊,带下', '煎服', '6-12g', '无水湿者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.4, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '猪苓';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('车前草', '车轮草、猪耳草', '利水渗湿药', '寒', '甘', '归肝、肾、肺、小肠经', '清热利尿，祛痰，凉血，解毒', '水肿胀满,热淋涩痛,暑湿泄泻,血热吐衄,痰热咳嗽,痈肿疮毒', '煎服', '9-30g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '车前草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('田基黄', '地耳草、黄花草', '利水渗湿药', '凉', '甘、微苦', '归肝、胆经', '利湿退黄，清热解毒，活血消肿', '湿热黄疸,胁痛,泄泻,痢疾,痈疖肿痛,跌打损伤', '煎服', '15-30g', '', '外用适量', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '田基黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('叶下珠', '珍珠草、夜合草', '利水渗湿药', '凉', '甘、苦', '归肝、肺经', '清热解毒，利水消肿，明目，消积', '痢疾,泄泻,黄疸,水肿,热淋,石淋,目赤,夜盲,疳积', '煎服', '15-30g', '', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '叶下珠';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鸡骨草', '广州相思子、黄头草', '利水渗湿药', '凉', '甘、微苦', '归肝、胃经', '利湿退黄，清热解毒，疏肝止痛', '湿热黄疸,胁肋不舒,胃脘胀痛,乳痈肿痛', '煎服', '15-30g', '种子有毒,用时须将豆荚全部摘除', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鸡骨草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('赤小豆', '红小豆、饭赤豆', '利水渗湿药', '平', '甘、酸', '归心、小肠经', '利水消肿，解毒排脓', '水肿胀满,脚气浮肿,黄疸尿赤,痈肿疮毒,肠痈腹痛', '煎服', '9-30g', '阴津不足者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '赤小豆';

-- ======================== 理气药（6 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('柿蒂', '柿钱、柿丁', '理气药', '平', '苦、涩', '归胃经', '降逆止呃', '呃逆', '煎服', '4.5-9g', '', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '柿蒂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('刀豆', '挟剑豆、刀豆子', '理气药', '温', '甘', '归胃、肾经', '温中，下气，止呃', '虚寒呃逆,呕吐,肾虚腰痛', '煎服', '6-9g', '胃热盛者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '刀豆';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('化橘红', '化州橘红、化红', '理气药', '温', '辛、苦', '归肺、脾经', '理气宽中，燥湿化痰', '咳嗽痰多,食积伤酒,呕恶痞闷', '煎服', '3-6g', '阴虚燥咳、久咳气虚者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.8, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '化橘红';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('橘红', '芸皮、芸红', '理气药', '温', '辛、苦', '归肺、脾经', '理气宽中，燥湿化痰', '咳嗽痰多,胸闷,食积,呕吐', '煎服', '3-6g', '阴虚燥咳、久咳气虚者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '橘红';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('川木香', '木香、铁杆木香', '理气药', '温', '辛、苦', '归脾、胃、大肠、胆经', '行气止痛', '肝胃气痛,脘腹胀痛,胁痛,里急后重,呕吐,泄泻', '煎服', '3-9g', '阴虚津亏者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '川木香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('八月札', '预知子、燕蓄子', '理气药', '寒', '甘', '归肝、胃经', '疏肝理气，活血止痛，散结，利尿', '脘胁胀痛,痛经经闭,痰核痞块,小便不利', '煎服', '3-9g', '孕妇慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '八月札';

-- ======================== 消食药（1 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('稻芽', '谷芽、南谷芽', '消食药', '平', '甘', '归脾、胃经', '消食和中，健脾开胃', '食积不消,腹胀口臭,脾胃虚弱,不饥食少', '煎服', '9-15g', '', '炒稻芽偏于消食,焦稻芽善化积滞', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.05, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '稻芽';

-- ======================== 止血药（12 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('三七', '田七、参三七', '止血药', '温', '甘、微苦', '归肝、胃经', '散瘀止血，消肿定痛', '咯血,吐血,衄血,便血,崩漏,外伤出血,胸腹刺痛,跌扑肿痛', '研粉吞服', '1-3g', '孕妇慎服', '煎服则 3-9g,研粉止血效佳', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 3.0, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '三七';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('大蓟', '大刺儿菜、虎蓟', '止血药', '凉', '甘、苦', '归心、肝经', '凉血止血，散瘀解毒消痈', '衄血,吐血,尿血,便血,崩漏,外伤出血,痈肿疮毒', '煎服', '9-15g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.1, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '大蓟';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('小蓟', '刺儿菜、青刺蓟', '止血药', '凉', '甘、苦', '归心、肝经', '凉血止血，散瘀解毒消痈', '衄血,吐血,尿血,血淋,便血,崩漏,外伤出血,痈肿疮毒', '煎服', '9-15g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.1, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '小蓟';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('地榆', '猪人参、血箭草', '止血药', '微寒', '苦、酸、涩', '归肝、大肠经', '凉血止血，解毒敛疮', '便血,痔血,血痢,崩漏,水火烫伤,痈肿疮毒', '煎服', '9-15g', '虚寒性出血慎用,大面积烧烫伤不宜外涂', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '地榆';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('槐花', '槐蕊、槐米', '止血药', '微寒', '苦', '归肝、大肠经', '凉血止血，清肝泻火', '便血,痔血,血痢,崩漏,吐血,衄血,肝热目赤,头痛眩晕', '煎服', '5-10g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '槐花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('槐角', '槐实、槐子', '止血药', '寒', '苦', '归肝、大肠经', '清热泻火，凉血止血', '肠热便血,痔肿出血,肝热头痛,眩晕目赤', '煎服', '6-9g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '槐角';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('侧柏叶', '柏叶、丛柏叶', '止血药', '寒', '苦、涩', '归肺、肝、脾经', '凉血止血，化痰止咳，生发乌发', '吐血,衄血,咯血,便血,崩漏下血,肺热咳嗽,血热脱发,须发早白', '煎服', '6-12g', '寒嗽虚咳者慎服', '外用适量', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.06, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '侧柏叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白茅根', '茅根、丝茅草', '止血药', '寒', '甘', '归肺、胃、膀胱经', '凉血止血，清热利尿', '血热吐血,衄血,尿血,热病烦渴,湿热黄疸,水肿尿少,热淋涩痛', '煎服', '9-30g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白茅根';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('茜草', '血见愁、红茜草', '止血药', '寒', '苦', '归肝经', '凉血止血，祛瘀，通经', '吐血,衄血,崩漏,外伤出血,瘀阻经闭,关节痹痛,跌扑肿痛', '煎服', '6-10g', '脾胃虚寒者慎服', '止血炒炭用,活血通经生用', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '茜草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蒲黄', '蒲棒粉、蒲厘花粉', '止血药', '平', '甘', '归肝、心包经', '止血，化瘀，通淋', '吐血,衄血,咯血,崩漏,外伤出血,经闭痛经,脘腹刺痛,血淋涩痛', '包煎', '5-10g', '孕妇慎服', '外用适量', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.3, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蒲黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('炮姜', '黑姜、姜炭', '止血药', '热', '辛', '归脾、胃、肾经', '温经止血，温中止痛', '阳虚失血,吐衄崩漏,脾胃虚寒,腹痛吐泻', '煎服', '3-9g', '阴虚内热、血热妄行者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '炮姜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('苎麻根', '家苎麻、野麻根', '止血药', '寒', '甘', '归心、肝、肾、膀胱经', '凉血止血，安胎，清热解毒', '血热出血,胎动不安,胎漏下血,痈肿疮毒,热淋涩痛', '煎服', '9-30g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.1, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '苎麻根';

-- ======================== 活血化瘀药（5 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('三棱', '荆三棱、京三棱', '活血化瘀药', '平', '辛、苦', '归肝、脾经', '破血行气，消积止痛', '癥瘕痞块,痛经,瘀血经闭,胸痹心痛,食积胀痛', '醋炙用,煎服', '5-10g', '月经过多者及孕妇忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '三棱';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('莪术', '文术、广莪术', '活血化瘀药', '温', '辛、苦', '归肝、脾经', '行气破血，消积止痛', '癥瘕痞块,瘀血经闭,胸痹心痛,食积胀痛', '醋炙用,煎服', '6-10g', '月经过多者及孕妇忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '莪术';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('泽兰', '地笋、虎兰', '活血化瘀药', '平', '苦、辛', '归肝、脾经', '活血调经，祛瘀消痈，利水消肿', '月经不调,经闭,痛经,产后瘀血腹痛,疮痈肿毒,水肿腹水', '煎服', '6-12g', '血虚者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.1, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '泽兰';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('月季花', '月月红、长春花', '活血化瘀药', '温', '甘', '归肝经', '活血调经，疏肝解郁', '气滞血瘀,月经不调,痛经,闭经,胸腹胀痛', '煎服', '3-6g', '孕妇及脾胃便溏者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.3, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '月季花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('凌霄花', '紫葳、堕胎花', '活血化瘀药', '寒', '辛', '归肝、心包经', '活血通经，凉血祛风', '月经不调,经闭痛经,产后乳肿,风疹发红,皮肤瘙痒,痤疮', '煎服', '5-9g', '孕妇忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.3, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '凌霄花';

-- ======================== 化痰止咳平喘药（5 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('黄药子', '黄独、零余薯', '化痰止咳平喘药', '平', '苦', '归肺、肝经', '化痰散结，清热解毒，凉血止血', '瘿瘤,疮疡肿毒,咽喉肿痛,毒蛇咬伤,吐血衄血', '煎服', '3-9g', '本品有毒,过量可致肝损伤,不宜久服,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '黄药子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('瓦楞子', '蚶壳、瓦屋子', '化痰止咳平喘药', '平', '咸', '归肺、胃、肝经', '消痰化瘀，软坚散结，制酸止痛', '顽痰胶结,黏稠难咯,瘿瘤,瘰疬,癥瘕痞块,胃痛泛酸', '先煎', '9-15g', '无痰积者不宜用', '消痰软坚生用,制酸止痛煅用', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.05, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '瓦楞子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('罗汉果', '拉汗果、假苦瓜', '化痰止咳平喘药', '凉', '甘', '归肺、大肠经', '清热润肺，利咽开音，滑肠通便', '肺热燥咳,咽痛失音,肠燥便秘', '煎服', '9-15g', '风寒咳嗽者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.6, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '罗汉果';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('冬瓜子', '白瓜子、瓜瓣', '化痰止咳平喘药', '凉', '甘', '归肺、大肠经', '清热化痰，排脓，利湿', '痰热咳嗽,肺痈吐脓,肠痈腹痛,淋浊,带下,水肿', '煎服', '9-30g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '冬瓜子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('矮地茶', '紫金牛、平地木', '化痰止咳平喘药', '平', '苦、辛', '归肺、肝经', '化痰止咳，清利湿热，活血化瘀', '新久咳嗽,喘满痰多,湿热黄疸,经闭瘀阻,风湿痹痛,跌打损伤', '煎服', '15-30g', '', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '矮地茶';

-- ======================== 平肝息风药（4 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蜈蚣', '天龙、百脚', '平肝息风药', '温', '辛', '归肝经', '息风镇痉，通络止痛，攻毒散结', '肝风内动,痉挛抽搐,小儿惊风,中风口喎,半身不遂,破伤风,风湿顽痹,偏正头痛,疮疡,瘰疬,蛇虫咬伤', '煎服', '3-5g', '孕妇忌服', '研末吞服 0.6-1g', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 1.5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蜈蚣';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('全蝎', '全虫、蝎子', '平肝息风药', '平', '辛', '归肝经', '息风镇痉，通络止痛，攻毒散结', '肝风内动,痉挛抽搐,小儿惊风,中风口喎,半身不遂,破伤风,风湿顽痹,偏正头痛,疮疡,瘰疬', '煎服', '3-6g', '孕妇忌服', '研末吞服 0.6-1g', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 2.5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '全蝎';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('僵蚕', '天虫、僵虫', '平肝息风药', '平', '咸、辛', '归肝、肺、胃经', '息风止痉，祛风止痛，化痰散结', '肝风夹痰,惊痫抽搐,小儿急惊风,中风口喎,风热头痛,目赤咽痛,风疹瘙痒,瘰疬痰核', '煎服', '5-10g', '血虚生风者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.6, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '僵蚕';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('地龙', '蚯蚓、曲鳝', '平肝息风药', '寒', '咸', '归肝、脾、膀胱经', '清热定惊，通络，平喘，利尿', '高热神昏,惊痫抽搐,关节痹痛,肢体麻木,半身不遂,肺热喘咳,水肿尿少', '煎服', '5-10g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.3, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '地龙';

-- ======================== 开窍药（4 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('麝香', '元寸、当门子', '开窍药', '温', '辛', '归心、脾经', '开窍醒神，活血通经，消肿止痛', '热病神昏,中风痰厥,气郁暴厥,中恶昏迷,经闭,癥瘕,难产死胎,跌扑伤痛,痈肿瘰疬,咽喉肿痛', '入丸散', '0.03-0.1g', '孕妇禁用', '不入煎剂,现多用人工麝香', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 9.9, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '麝香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('苏合香', '苏合油、帝膏', '开窍药', '温', '辛', '归心、脾经', '开窍醒神，辟秽，止痛', '中风痰厥,猝然昏倒,惊痫,胸痹心痛,胸腹冷痛', '入丸散', '0.3-1g', '热闭证及气阴虚者慎服', '不入煎剂', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 2.0, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '苏合香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('石菖蒲', '菖蒲、九节菖蒲', '开窍药', '温', '辛、苦', '归心、胃经', '开窍豁痰，醒神益智，化湿开胃', '神昏癫痫,健忘失眠,耳鸣耳聋,脘痞不饥,噤口下痢', '煎服', '3-10g', '阴虚阳亢者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.3, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '石菖蒲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('安息香', '白胶香、拙贝罗香', '开窍药', '平', '辛、苦', '归心、脾经', '开窍醒神，行气活血，止痛', '中风痰厥,气郁暴厥,中恶昏迷,产后血晕,心腹疼痛', '入丸散', '0.6-1.5g', '热闭证慎服', '不入煎剂', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 1.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '安息香';

-- ======================== 补虚药（4 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('饴糖', '麦芽糖、胶饴', '补虚药', '温', '甘', '归脾、胃、肺经', '补中益气，缓急止痛，润肺止咳', '中虚脘痛,肺燥咳嗽', '烊化冲入', '15-20g', '湿热内郁、中满吐逆者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.05, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '饴糖';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鹿角', '斑龙角', '补虚药', '温', '咸', '归肝、肾经', '温肾阳，强筋骨，行血消肿', '肾阳不足,阳痿遗精,腰脊冷痛,阴疽疮疡,乳痈初起,瘀血肿痛', '煎服', '6-15g', '阴虚火旺者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鹿角';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鹿角胶', '白胶、鹿胶', '补虚药', '温', '甘、咸', '归肝、肾经', '温补肝肾，益精养血', '肝肾不足所致腰膝酸冷,阳痿遗精,虚劳羸瘦,崩漏下血,便血尿血,阴疽肿痛', '烊化兑服', '5-15g', '阴虚火旺者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 1.5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鹿角胶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鹿角霜', '鹿角白霜', '补虚药', '温', '咸、涩', '归肝、肾经', '温肾助阳，收敛止血', '脾肾阳虚,食少吐泻,白带,遗尿尿频,崩漏下血,痈疽疮疡', '先煎', '9-15g', '阴虚火旺者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.4, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鹿角霜';

-- ======================== 收涩药（12 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('五味子', '玄及、五梅子', '收涩药', '温', '酸、甘', '归肺、心、肾经', '收敛固涩，益气生津，补肾宁心', '久嗽虚喘,梦遗滑精,遗尿尿频,久泻不止,自汗盗汗,津伤口渴,内热消渴,心悸失眠', '煎服', '2-6g', '表邪未解、内有实热,咳嗽初起,麻疹初发者均慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.9, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '五味子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('乌梅', '梅实、酸梅', '收涩药', '平', '酸、涩', '归肝、脾、肺、大肠经', '敛肺，涩肠，生津，安蛔', '肺虚久咳,久泻久痢,虚热消渴,蛔厥呕吐腹痛', '煎服', '6-12g', '外有表邪或内有实热积滞者均不宜服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '乌梅';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桑螵蛸', '螳螂子、刀螂子', '收涩药', '平', '甘、咸', '归肝、肾经', '固精缩尿，补肾助阳', '遗精滑精,遗尿尿频,小便白浊', '煎服', '5-10g', '阴虚火旺或膀胱有热者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.4, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桑螵蛸';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('海螵蛸', '乌贼骨、乌鲗骨', '收涩药', '温', '咸、涩', '归脾、肾经', '收敛止血，涩精止带，制酸止痛，收湿敛疮', '吐血衄血,崩漏便血,遗精滑精,赤白带下,胃痛吞酸,外伤出血,湿疹湿疮,溃疡不敛', '煎服', '5-10g', '阴虚多热者不宜多服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '海螵蛸';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('金樱子', '刺榆子、金罂子', '收涩药', '平', '酸、甘、涩', '归肾、膀胱、大肠经', '固精缩尿，固崩止带，涩肠止泻', '遗精滑精,遗尿尿频,崩漏带下,久泻久痢', '煎服', '6-12g', '有实火、邪热者不宜服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '金樱子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('芡实', '鸡头米、雁头米', '收涩药', '平', '甘、涩', '归脾、肾经', '益肾固精，补脾止泻，除湿止带', '遗精滑精,遗尿尿频,脾虚久泻,白浊,带下', '煎服', '9-15g', '便秘、产后及大小便不利者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.2, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '芡实';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('覆盆子', '覆盆、小托盘', '收涩药', '温', '甘、酸', '归肝、肾、膀胱经', '益肾固精缩尿，养肝明目', '遗精滑精,遗尿尿频,阳痿早泄,目暗昏花', '煎服', '6-12g', '肾虚有火、小便短涩者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '覆盆子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('莲须', '白莲须、莲花须', '收涩药', '平', '甘、涩', '归心、肾经', '固肾涩精', '遗精滑精,带下,尿频', '煎服', '3-5g', '小便不利者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.3, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '莲须';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('赤石脂', '赤符、红高岭', '收涩药', '温', '甘、酸、涩', '归大肠、胃经', '涩肠止泻，收敛止血，生肌敛疮', '久泻久痢,大便滑脱不禁,便血带血,崩漏,疮疡久溃不敛', '先煎', '9-12g', '湿热积滞者忌服,孕妇慎服', '不宜与官桂同用', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '赤石脂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('禹余粮', '禹粮石、余粮石', '收涩药', '微寒', '甘、涩', '归胃、大肠经', '涩肠止泻，收敛止血，止带', '久泻久痢,大便出血,崩漏带下', '先煎', '9-15g', '实证热证及孕妇慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '禹余粮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('麻黄根', '苦椿菜、止汗草', '收涩药', '平', '甘、微涩', '归心、肺经', '固表止汗', '自汗,盗汗', '煎服', '3-9g', '有表邪者忌服', '外用研粉扑身止汗', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '麻黄根';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('浮小麦', '浮麦、瘪麦', '收涩药', '凉', '甘', '归心经', '固表止汗，益气，除热', '自汗,盗汗,阴虚发热,骨蒸劳热', '煎服', '15-30g', '无汗而烦躁者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.05, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '浮小麦';

-- ======================== 涌吐药（1 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('常山', '鸡骨常山、黄常山', '涌吐药', '寒', '苦、辛', '归肺、肝、心经', '涌吐痰涎，截疟', '痰饮停聚,胸膈痞塞,疟疾', '煎服', '4.5-9g', '正气不足,久病体弱者及孕妇慎服', '截疟宜在疟发前 2 小时服药', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '常山';

-- ======================== 攻毒杀虫止痒药（5 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('大蒜', '蒜头、胡蒜', '攻毒杀虫止痒药', '温', '辛', '归脾、胃、肺经', '解毒消肿，杀虫，止痢', '痈肿疮疡,疥癣,肺痨,顿咳,泄泻,痢疾', '煎服', '9-15g', '阴虚火旺及目疾、口齿喉舌疾患者慎食', '生食或外用', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.05, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '大蒜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('斑蝥', '斑猫、龙尾', '攻毒杀虫止痒药', '热', '辛', '归肝、胃、肾经', '破血逐瘀，散结消癥，攻毒蚀疮', '癥瘕,经闭,顽癣,瘰疬,赘疣,痈疽不溃,恶疮死肌', '炮制后入丸散', '0.03-0.06g', '有大毒,内服宜慎,体弱及孕妇禁服,心肾功能不全者禁服', '外用适量,不宜大面积涂擦', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.8, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '斑蝥';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('轻粉', '水银粉、汞粉', '攻毒杀虫止痒药', '寒', '辛', '归大肠、小肠经', '外用杀虫，攻毒，敛疮；内服祛痰消积，逐水通便', '疥疮,顽癣,梅毒,疮疡,湿疹,痰涎积滞,水肿臌胀,二便不利', '外用适量；内服入丸散', '0.1-0.2g', '有毒,内服宜慎,体弱及孕妇禁服', '外用不可久涂', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '轻粉';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('大风子', '大枫子、麻风子', '攻毒杀虫止痒药', '热', '辛', '归肝、脾、肾经', '祛风燥湿，攻毒杀虫', '麻风,疥癣,杨梅恶疮', '外用适量', '外用为主', '本品有毒,内服宜慎,孕妇禁服', '多外用捣敷或煅存性研末调敷', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.3, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '大风子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('升药', '红升丹、三仙丹', '攻毒杀虫止痒药', '热', '辛', '归肺、脾经', '拔毒排脓，去腐生肌', '痈疽溃后,脓出不畅,腐肉不去,新肉难生', '外用适量', '只供外用', '本品有毒,腐蚀性较强,只供外用,不作内服,孕妇及体弱者忌用', '常与煅石膏配伍研末外用', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.6, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '升药';

-- ======================== 其他常用（2 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('荷叶', '莲叶、干荷叶', '清热药', '平', '苦', '归肝、脾、胃经', '清暑化湿，升发清阳，凉血止血', '暑热烦渴,暑湿泄泻,脾虚泄泻,血热吐衄,便血崩漏', '煎服', '3-10g', '气血虚者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '荷叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('椿皮', '椿根皮、臭椿皮', '清热药', '寒', '苦、涩', '归大肠、胃、肝经', '清热燥湿，收涩止带，止泻，止血', '赤白带下,湿热泻痢,久泻久痢,便血,崩漏', '煎服', '6-9g', '脾胃虚寒者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.1, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '椿皮';
