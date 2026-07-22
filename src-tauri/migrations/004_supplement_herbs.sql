-- =====================================================================
-- 004_supplement_herbs.sql
-- 中药材销售管理系统 - 方剂模板引用补充药材入库
-- 用途：22 个方剂模板中引用但 002_seed_medicines.sql 中 300 味种子库缺失的药材补充
-- 数据来源：《中药学》教材
-- 生成时间：2026-07-22
-- 库存初始化：quantity=1000, unit='g', price=各药材定价, min_stock=100
-- 时间戳：created_at/updated_at 统一使用 '2026-07-17 00:00:00'
-- 使用 INSERT OR IGNORE 避免与已有数据冲突
-- 每味药材对应 2 条 SQL：medicines INSERT + inventory INSERT...SELECT
-- 共补充 19 味药材（17 味原方剂模板缺失 + 2 味新增方剂模板缺失）
-- 说明：以下药材虽与种子库中部分药材名称相近，但为不同炮制品/入药部位，
--       属于独立药材条目（如炙甘草/生甘草、生白芍/白芍、霜桑叶/桑叶、
--       朱茯神/茯神等）；其中杏仁、龙胆草、川牛膝在 002 中以别名形式收录
--       于苦杏仁、龙胆、牛膝条目下，此处按方剂模板引用名独立建条，
--       以支撑按精确名称查询。
-- 注：大枣、淡豆豉、生地黄因 002 种子库中已有同名条目，本文件不再重复录入。
-- =====================================================================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('炙甘草', '蜜甘草、炙草', '补虚药', '温', '甘', '归心、肺、脾、胃经', '补脾和胃,益气复脉', '脾胃虚弱,倦怠乏力,心动悸脉结代', '煎服', '3-9g', '湿盛胀满者不宜', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '炙甘草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('生姜', '鲜姜', '解表药', '温', '辛', '归肺、脾、胃经', '解表散寒,温中止呕,化痰止咳', '风寒感冒,脾胃寒证,胃寒呕吐,寒痰咳嗽', '煎服', '3-10g', '阴虚内热者慎用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 8, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '生姜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('杏仁', '苦杏仁、北杏仁', '止咳平喘药', '微温', '苦', '归肺、大肠经', '降气止咳平喘,润肠通便', '咳嗽气喘,胸满痰多,肠燥便秘', '煎服', '5-10g', '阴虚咳嗽及大便溏泄者慎服', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '杏仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('荆芥穗', '荆芥炭穗', '解表药', '微温', '辛', '归肺、肝经', '解表散风,透疹消疮', '风寒感冒,头痛,麻疹不透,疮疡初起', '煎服', '5-10g', '表虚自汗者忌服', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 18, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '荆芥穗';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('粳米', '大米', '补虚药', '平', '甘', '归脾、胃经', '补中益气,健脾和胃', '脾胃虚弱,烦渴,泄泻', '煎服', '30-50g', '无特殊禁忌', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 5, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '粳米';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('山茱萸', '山萸肉、枣皮', '收涩药', '微温', '酸、涩', '归肝、肾经', '补益肝肾,收涩固脱', '眩晕耳鸣,腰膝酸痛,阳痿遗精,遗尿尿频', '煎服', '6-12g', '命门火炽,湿热内盛者不宜', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '山茱萸';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('龙胆草', '龙胆、胆草', '清热药', '寒', '苦', '归肝、胆经', '清热燥湿,泻肝胆火', '湿热黄疸,阴肿阴痒,带下,湿疹瘙痒,目赤,耳聋,胁痛,口苦,惊风抽搐', '煎服', '3-6g', '脾胃虚寒者不宜,阴虚津伤者慎用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 22, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '龙胆草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('生甘草', '生草、粉甘草', '补虚药', '平', '甘', '归心、肺、脾、胃经', '补脾益气,清热解毒,祛痰止咳', '脾胃虚弱,倦怠乏力,咳嗽痰多,痈肿疮毒', '煎服', '2-10g', '不宜与京大戟、芫花、甘遂同用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '生甘草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('生白芍', '生芍药', '补虚药', '微寒', '苦、酸', '归肝、脾经', '养血调经,敛阴止汗,柔肝止痛', '血虚萎黄,月经不调,自汗盗汗,胁痛腹痛,四肢挛急', '煎服', '6-15g', '阳衰虚寒之证不宜用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 28, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '生白芍';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('霜桑叶', '冬桑叶、经霜桑叶', '解表药', '寒', '甘、苦', '归肺、肝经', '疏散风热,清肺润燥,平抑肝阳,清肝明目', '风热感冒,肺热燥咳,头晕头痛,目赤昏花', '煎服', '5-10g', '无特殊禁忌', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 14, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '霜桑叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('茯神', '伏神', '安神药', '平', '甘、淡', '归心、脾、肾经', '宁心安神', '心悸怔忡,失眠健忘,惊痫', '煎服', '10-15g', '阴虚而无湿热者慎用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '茯神';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('朱茯神', '朱砂拌茯神', '安神药', '平', '甘、淡', '归心、脾、肾经', '宁心安神,镇惊', '心悸怔忡,失眠惊痫', '煎服', '10-15g', '阴虚而无湿热者慎用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 32, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '朱茯神';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('川牛膝', '川膝', '活血化瘀药', '平', '苦、甘', '归肝、肾经', '逐瘀通经,通利关节,利尿通淋', '经闭癥瘕,胞衣不下,关节痹痛,足痿筋挛,尿血血淋,跌扑损伤', '煎服', '5-10g', '孕妇禁用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 26, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '川牛膝';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('大腹皮', '槟榔皮、大腹毛', '理气药', '微温', '辛', '归脾、胃、大肠、小肠经', '行气宽中,行水消肿', '湿阻气滞,脘腹胀闷,大便不爽,水肿胀满,脚气浮肿,小便不利', '煎服', '5-10g', '气虚体弱者慎用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 16, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '大腹皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('半夏曲', '法半夏曲', '化痰止咳平喘药', '温', '辛', '归脾、胃、肺经', '燥湿化痰,消食止呕', '湿痰咳嗽,胸脘痞闷,呕吐食少', '煎服', '5-10g', '阴虚燥咳者不宜', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '半夏曲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('羚羊角片', '羚羊角', '平肝息风药', '寒', '咸', '归肝、心经', '平肝息风,清肝明目,凉血解毒', '肝风内动,惊痫抽搐,肝阳上亢,头晕目眩,肝火上炎,目赤头痛,温热病壮热神昏', '煎服或磨汁服', '1-3g', '脾虚慢惊者忌用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 120, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '羚羊角片';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫苏', '紫苏叶、苏叶', '解表药', '温', '辛', '归肺、脾经', '解表散寒,行气和胃', '风寒感冒,咳嗽呕恶,妊娠呕吐,鱼蟹中毒', '煎服', '5-10g', '无特殊禁忌', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '紫苏';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('代赭石', '赭石、钉头赭石', '平肝息风药', '寒', '苦', '归肝、心经', '平肝潜阳,重镇降逆,凉血止血', '头痛眩晕,呕吐噫气,呃逆,喘息,吐血,衄血,崩漏下血', '煎服,先煎', '10-30g', '孕妇慎用', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 18, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '代赭石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('莲子肉', '莲子、莲肉', '收涩药', '平', '甘、涩', '归脾、肾、心经', '补脾止泻,止带,养心安神,益肾固精', '脾虚泄泻,带下,遗精,心悸,失眠', '煎服', '6-15g', '中满痞胀及大便燥结者忌服', '补充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '莲子肉';
