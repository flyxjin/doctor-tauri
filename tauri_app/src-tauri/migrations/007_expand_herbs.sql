-- =====================================================================
-- 007_expand_herbs.sql
-- 中药材销售管理系统 - 扩充药材库（81 味常用中药）
-- 用途：在 002(300味) + 004(19味) 共 319 味基础上补充 81 味常用中药材，
--       覆盖清热、祛风湿、利水渗湿、温里、理气、消食、驱虫、止血、
--       活血化瘀、化痰止咳、安神、平肝息风、开窍、补虚、收涩、
--       攻毒杀虫止痒、拔毒化腐生肌等分类，使总数达到 400 味。
-- 数据来源：《中药学》教材 + 《中国药典》
-- 生成时间：2026-07-23
-- 价格单位：元/g（与 006_fix_price_unit.sql 修复后基准一致）
-- 库存初始化：quantity=1000, unit='g', min_stock=100
-- 时间戳：created_at/updated_at 统一使用 '2026-07-17 00:00:00'
-- 使用 INSERT OR IGNORE 避免与已有数据冲突
-- 每味药材对应 2 条 SQL：medicines INSERT + inventory INSERT...SELECT
-- =====================================================================

-- ======================== 清热药（15 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('青葙子', '草决明、野鸡冠花子', '清热药', '微寒', '苦', '归肝经', '清肝泻火,明目退翳', '肝热目赤,目生翳膜,视物昏花,肝火眩晕', '煎服', '9-15g', '本品有扩散瞳孔作用,青光眼患者忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '青葙子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白蔹', '山地瓜、野红薯', '清热药', '微寒', '苦、辛', '归心、胃经', '清热解毒,消痈散结,敛疮生肌', '痈疽发背,疔疮,瘰疬,烧烫伤', '煎服', '5-10g', '脾胃虚寒者不宜服,反乌头', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.40, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '白蔹';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('山慈菇', '毛慈菇、冰球子', '清热药', '凉', '甘、微辛', '归肝、脾经', '清热解毒,化痰散结', '痈肿疔毒,瘰疬痰核,蛇虫咬伤,癥瘕痞块', '煎服', '3-9g', '正虚体弱者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.85, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '山慈菇';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('绿豆', '青小豆', '清热药', '寒', '甘', '归心、胃经', '清热解毒,消暑利水', '暑热烦渴,药食中毒,水肿,小便不利', '煎服', '15-30g', '脾胃虚寒肠滑泄泻者忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.05, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '绿豆';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('木蝴蝶', '千层纸、玉蝴蝶', '清热药', '寒', '苦、甘', '归肺、肝、胃经', '清肺利咽,疏肝和胃', '肺热咳嗽,喉痹音哑,肝胃气痛', '煎服', '1.5-3g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '木蝴蝶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('半边莲', '急解索、细米草', '清热药', '寒', '辛', '归心、小肠、肺经', '清热解毒,利水消肿', '疮痈肿毒,蛇虫咬伤,鼓胀水肿,黄疸尿少', '煎服', '9-15g', '虚证水肿忌用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '半边莲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白英', '蜀羊泉、白毛藤', '清热药', '寒', '苦、微辛', '归肝、胆经', '清热解毒,祛风除湿', '湿热黄疸,疮痈肿毒,风湿痹痛,癌症', '煎服', '15-30g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '白英';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('龙葵', '苦葵、天茄子', '清热药', '寒', '苦、微甘', '归肺、膀胱经', '清热解毒,利尿消肿', '疮痈肿毒,皮肤湿疹,小便不利,水肿,癌症', '煎服', '15-30g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.18, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '龙葵';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('三颗针', '铜针刺、小檗', '清热药', '寒', '苦', '归肝、胃、大肠经', '清热燥湿,泻火解毒', '湿热泻痢,黄疸,疮痈肿毒,咽喉肿痛,目赤肿痛', '煎服', '9-15g', '脾胃虚寒者慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.22, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '三颗针';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('马鞭草', '铁马鞭、紫顶龙芽', '清热药', '凉', '苦', '归肝、脾经', '清热解毒,活血散瘀,利水消肿', '湿热黄疸,泻痢,疟疾,疮痈肿毒,经闭痛经,水肿尿少', '煎服', '5-10g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '马鞭草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('半枝莲', '并头草、牙刷草', '清热药', '寒', '辛、苦', '归肺、肝、肾经', '清热解毒,化瘀利尿', '疔疮肿毒,咽喉肿痛,水肿,黄疸,蛇虫咬伤,癌症', '煎服', '15-30g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '半枝莲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('地锦草', '血见愁、铺地锦', '清热药', '平', '苦、辛', '归肝、大肠经', '清热解毒,凉血止血', '热毒泻痢,便血痔血,疮痈肿毒,蛇虫咬伤', '煎服', '9-20g', '血虚无瘀者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.16, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '地锦草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('翻白草', '鸡腿根、天藕', '清热药', '平', '甘、微苦', '归肝、大肠经', '清热解毒,止血,消肿', '湿热泻痢,痈肿疮毒,血热出血,肺热咳嗽', '煎服', '9-15g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.14, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '翻白草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鬼针草', '婆婆针、鬼钗草', '清热药', '平', '苦', '归肝、肺、大肠经', '清热解毒,祛风活血,消肿', '湿热泻痢,疮痈肿毒,蛇虫咬伤,跌打损伤,风湿痹痛', '煎服', '15-30g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '鬼针草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('垂盆草', '狗牙瓣、石指甲', '清热药', '凉', '甘、淡', '归肝、胆、小肠经', '清热解毒,利湿退黄', '湿热黄疸,小便不利,疮痈肿毒,水火烫伤,蛇虫咬伤', '煎服', '15-30g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.18, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '垂盆草';

-- ======================== 泻下药（1 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('红大戟', '红芽大戟、紫大戟', '泻下药', '寒', '苦', '归肺、脾、肾经', '泻水逐饮,消肿散结', '水肿胀满,胸腹积水,痰饮积聚,痈肿疮毒', '煎服', '1.5-3g', '孕妇禁用,体虚者慎用,不宜与甘草同用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.45, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '红大戟';

-- ======================== 祛风湿药（5 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('两面针', '入地金牛、双面针', '祛风湿药', '平', '苦、辛', '归肝、胃经', '祛风通络,活血止痛,解毒消肿', '风湿痹痛,胃痛牙痛,跌扑损伤,毒蛇咬伤', '煎服', '5-10g', '孕妇忌服,服用过量可致头晕眼花', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.28, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '两面针';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('海桐皮', '刺桐皮、钉桐皮', '祛风湿药', '平', '苦、辛', '归肝经', '祛风除湿,通络止痛,杀虫止痒', '风湿痹痛,四肢拘挛,腰膝疼痛,疥癣湿疹', '煎服', '5-15g', '血虚者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '海桐皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('臭梧桐', '海州常山、八角梧桐', '祛风湿药', '平', '辛、苦、甘', '归肝经', '祛风除湿,通络止痛,平肝降压', '风湿痹痛,肢体麻木,半身不遂,高血压', '煎服', '5-15g', '脾胃虚弱者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '臭梧桐';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('雪上一枝蒿', '铁棒锤、一枝蒿', '祛风湿药', '温', '苦、辛', '归肝经', '祛风除湿,活血止痛', '风湿痹痛,跌扑损伤,牙痛,术后疼痛', '煎服', '0.02-0.04g', '本品大毒,内服宜慎,孕妇禁服,炮制后入丸散', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 1.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '雪上一枝蒿';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('雷公藤', '黄藤根、断肠草', '祛风湿药', '寒', '苦、辛', '归肝、肾经', '祛风除湿,通络止痛,活血消肿,杀虫解毒', '风湿痹痛,关节肿痛,疔疮肿毒,腰带疮,麻风病', '煎服', '1-3g', '本品大毒,内服宜慎,孕妇禁服,心肝肾功能不全者慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '雷公藤';

-- ======================== 利水渗湿药（3 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('冬瓜皮', '白瓜皮', '利水渗湿药', '凉', '甘', '归脾、小肠经', '利水消肿', '水肿胀满,小便不利,暑热口渴', '煎服', '15-30g', '营养不良性水肿慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.06, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '冬瓜皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('玉米须', '包谷须、玉蜀黍须', '利水渗湿药', '平', '甘', '归膀胱、肝、胆经', '利水消肿,利湿退黄', '水肿,小便不利,黄疸,胆囊炎,胆结石,高血压', '煎服', '15-30g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.05, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '玉米须';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('虎杖', '花斑竹、酸汤杆', '利水渗湿药', '微寒', '苦', '归肝、胆、肺经', '利湿退黄,清热解毒,散瘀止痛,化痰止咳', '湿热黄疸,淋浊带下,水火烫伤,痈肿疮毒,毒蛇咬伤,经闭癥瘕,跌打损伤,肺热咳嗽', '煎服', '9-15g', '孕妇忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '虎杖';

-- ======================== 温里药（2 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('红豆蔻', '红蔻、良姜子', '温里药', '温', '辛', '归脾、肺经', '温中散寒,醒脾燥湿', '寒湿腹痛,呕吐泄泻,噎膈反胃', '煎服', '3-6g', '阴虚有热者忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '红豆蔻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('母丁香', '鸡舌香', '温里药', '温', '辛', '归脾、胃、肺、肾经', '温中降逆,散寒止痛,温肾助阳', '脾胃虚寒,呃逆呕吐,食少吐泻,心腹冷痛,肾虚阳痿', '煎服', '1-3g', '热证及阴虚火旺者忌服,畏郁金', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.45, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '母丁香';

-- ======================== 理气药（3 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('娑罗子', '梭罗子、开心果', '理气药', '温', '甘', '归肝、胃经', '疏肝理气,宽中和胃', '肝胃气滞,胸闷胁痛,脘腹胀痛,经前乳房胀痛', '煎服', '3-9g', '阴虚内热者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.40, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '娑罗子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('九香虫', '黑兜虫、瓜黑蝽', '理气药', '温', '咸', '归肝、脾、肾经', '理气止痛,温肾助阳', '肝胃气滞,胸胁胀痛,脘腹痞闷,阳痿膝冷腰痛', '煎服', '3-9g', '阴虚内热者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.55, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '九香虫';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('甘松', '香松、甘松香', '理气药', '温', '辛、甘', '归脾、胃经', '理气止痛,开郁醒脾', '脘腹闷胀,食欲不振,呕吐,思虑伤脾,牙痛', '煎服', '3-6g', '阴虚血燥者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '甘松';

-- ======================== 消食药（2 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鸡矢藤', '鸡屎藤、斑鸠饭', '消食药', '平', '甘、微苦', '归脾、胃、肝、肺经', '消食健胃,化痰止咳,清热解毒,止痛', '消化不良,小儿疳积,胃肠绞痛,黄疸,咳嗽,疮痈肿毒', '煎服', '15-30g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.10, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '鸡矢藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('阿魏', '阿虞、熏渠', '消食药', '温', '苦、辛', '归肝、脾、胃经', '消积化癥,散痞杀虫', '癥瘕痞块,肉食积滞,虫积腹痛', '煎服', '1-1.5g', '脾胃虚弱者忌服,孕妇禁服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.80, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '阿魏';

-- ======================== 驱虫药（4 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('雷丸', '雷实、竹苓', '驱虫药', '寒', '微苦', '归胃、大肠经', '杀虫消积', '绦虫病,钩虫病,蛔虫病,蛲虫病,小儿疳积', '研粉服', '15-21g', '脾胃虚寒者慎服,不宜煎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.60, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '雷丸';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鹤草芽', '龙芽草芽', '驱虫药', '凉', '苦、涩', '归肝、小肠、大肠经', '杀虫', '绦虫病', '研粉服', '30-45g', '不宜入煎剂', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '鹤草芽';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鹤虱', '北鹤虱、天名精', '驱虫药', '平', '苦、辛', '归脾、胃经', '杀虫消积', '蛔虫病,蛲虫病,绦虫病,虫积腹痛,小儿疳积', '煎服', '3-9g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '鹤虱';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('榧子', '香榧、玉榧', '驱虫药', '平', '甘', '归肺、胃、大肠经', '杀虫消积,润肠通便,润肺止咳', '钩虫病,蛔虫病,绦虫病,虫积腹痛,小儿疳积,肠燥便秘,肺燥咳嗽', '煎服', '9-15g', '脾虚泄泻者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '榧子';

-- ======================== 止血药（3 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫珠草', '紫珠、止血草', '止血药', '凉', '苦、涩', '归肝、肺、胃经', '凉血收敛止血,清热解毒', '衄血,咯血,吐血,便血,崩漏,外伤出血,烧烫伤,疮痈肿毒', '煎服', '10-15g', '虚寒性出血慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '紫珠草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('降香', '紫降香、降真香', '止血药', '温', '辛', '归肝、心经', '化瘀止血,理气止痛', '出血证,跌扑损伤,胸痹心痛,呕吐腹痛', '煎服', '3-6g', '阴虚血热者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.85, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '降香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('花蕊石', '花乳石、白云石', '止血药', '平', '酸、涩', '归肝经', '化瘀止血', '吐血,衄血,便血,崩漏,产妇血晕,跌扑损伤,金疮出血', '煎服', '4.5-9g', '孕妇忌服,无瘀滞者慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '花蕊石';

-- ======================== 活血化瘀药（5 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('夏天无', '伏生紫堇、无柄紫堇', '活血化瘀药', '温', '苦、微辛', '归肝经', '活血止痛,舒筋通络,祛风除湿', '中风偏瘫,半身不遂,跌扑损伤,风湿痹痛,坐骨神经痛', '煎服', '6-12g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.40, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '夏天无';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('西红花', '番红花、藏红花', '活血化瘀药', '寒', '甘', '归心、肝经', '活血化瘀,凉血解毒,解郁安神', '经闭癥瘕,产后瘀阻,温毒发斑,忧郁痞闷,惊悸发狂', '煎服', '1-3g', '孕妇忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 25.00, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '西红花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('儿茶', '孩儿茶、黑儿茶', '活血化瘀药', '微寒', '苦、涩', '归心、肺经', '活血疗伤,止血生肌,收湿敛疮,清肺化痰', '跌扑损伤,出血证,疮疡不敛,湿疹,湿疮,肺热咳嗽', '煎服', '1-3g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.55, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '儿茶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('自然铜', '接骨丹、铜矿石', '活血化瘀药', '平', '辛', '归肝经', '散瘀止痛,接骨疗伤', '跌扑损伤,骨折筋断,瘀肿疼痛', '煎服', '3-9g', '阴虚火旺者慎服,不宜久服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '自然铜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('苏木', '苏方木、红柴', '活血化瘀药', '平', '甘、咸、辛', '归心、肝经', '活血疗伤,祛瘀通经', '跌扑损伤,骨折筋伤,血滞经闭,产后瘀阻腹痛,痛经,心腹刺痛,痈肿疮毒', '煎服', '3-9g', '孕妇忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '苏木';

-- ======================== 化痰止咳平喘药（3 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('猪牙皂', '牙皂、小皂荚', '化痰止咳平喘药', '温', '辛、咸', '归肺、大肠经', '祛痰开窍,散结消肿', '中风口噤,昏迷不醒,癫痫痰盛,关窍不通,喉痹痰阻,顽痰咳喘,疮肿未溃', '煎服', '1-1.5g', '孕妇禁服,咯血及阴虚火旺者忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '猪牙皂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('猫爪草', '小毛茛、三散草', '化痰止咳平喘药', '温', '甘、辛', '归肝、肺经', '化痰散结,解毒消肿', '瘰疬痰核,疔疮,蛇虫咬伤,疟疾,偏头痛,牙痛', '煎服', '9-15g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '猫爪草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('胖大海', '安南子、大海子', '化痰止咳平喘药', '寒', '甘', '归肺、大肠经', '清热润肺,利咽开音,润肠通便', '肺热声哑,干咳无痰,咽喉干痛,热结便秘,头痛目赤', '开水泡服', '2-3枚', '脾胃虚寒泄泻者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.40, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '胖大海';

-- ======================== 安神药（3 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('珍珠', '真珠、濂珠', '安神药', '寒', '甘、咸', '归心、肝经', '安神定惊,明目消翳,解毒生肌', '惊悸失眠,惊风癫痫,目赤翳障,口舌生疮,咽喉腐烂,溃疡不敛', '研末服', '0.1-0.3g', '无特殊禁忌', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 80.00, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '珍珠';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('珍珠母', '珠母、明珠母', '安神药', '寒', '咸', '归肝、心经', '平肝潜阳,安神定惊,明目退翳', '头痛眩晕,惊悸失眠,癫痫惊风,目赤翳障,视物昏花', '煎服', '10-25g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '珍珠母';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('合欢花', '夜合花、乌绒', '安神药', '平', '甘', '归心、肝经', '解郁安神,活血消肿', '心神不安,忧郁失眠,肺痈疮肿,跌扑损伤', '煎服', '5-10g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '合欢花';

-- ======================== 平肝息风药（3 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫贝齿', '紫贝、文贝', '平肝息风药', '平', '咸', '归肝经', '平肝潜阳,镇惊安神,清肝明目', '肝阳眩晕,惊悸失眠,小儿高热抽搐,目赤翳障', '煎服', '10-15g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '紫贝齿';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('罗布麻叶', '红麻、茶叶花', '平肝息风药', '凉', '甘、苦', '归肝经', '平肝安神,清热利水', '肝阳眩晕,心悸失眠,浮肿尿少,高血压', '煎服', '6-12g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.18, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '罗布麻叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('刺蒺藜', '白蒺藜、蒺藜', '平肝息风药', '平', '苦、辛', '归肝经', '平肝疏肝,祛风明目', '肝阳上亢,头痛眩晕,肝郁胁痛,风热目赤,风疹瘙痒,白癜风', '煎服', '6-10g', '孕妇慎服,血虚气弱者慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '刺蒺藜';

-- ======================== 开窍药（2 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('冰片', '龙脑冰片、梅花冰片', '开窍药', '微寒', '辛、苦', '归心、脾、肺经', '开窍醒神,清热止痛', '热病神昏,惊厥,中风痰厥,中恶昏迷,喉痹口疮,目赤肿痛,耳道流脓,疮疡肿痛,水火烫伤', '入丸散', '0.15-0.3g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 3.50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '冰片';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('樟脑', '潮脑、韶脑', '开窍药', '热', '辛', '归心、脾经', '开窍辟秽,除湿杀虫,温散止痛', '痧胀腹痛,吐泻神昏,疥癣湿疮,瘙痒,龋齿牙痛,跌打损伤', '入丸散', '0.1-0.2g', '孕妇忌服,内服宜慎', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '樟脑';

-- ======================== 补虚药（5 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('海龙', '水雁、海蛇', '补虚药', '温', '甘', '归肝、肾经', '温肾壮阳,散结消肿', '肾虚阳痿,宫冷不孕,遗尿,虚喘,癥瘕积聚,跌打损伤,痈肿疔疮', '煎服', '3-9g', '阴虚火旺者忌服,孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 2.50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '海龙';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('明党参', '土人参、粉沙参', '补虚药', '微寒', '甘、微苦', '归肺、脾经', '润肺化痰,和胃,解毒', '肺燥咳嗽,津伤口渴,食少呕吐,疔毒疮疡', '煎服', '6-12g', '脾胃虚寒者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '明党参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('竹节参', '竹节三七、竹节人参', '补虚药', '温', '甘、微苦', '归肝、脾、肺经', '补虚强壮,止血散瘀', '病后虚弱,肺虚咳嗽,衄血,外伤出血,跌扑损伤,痈肿疮毒', '煎服', '6-9g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.80, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '竹节参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('红芪', '岩黄芪、晋芪', '补虚药', '微温', '甘', '归肺、脾经', '补气升阳,固表止汗,利水消肿,生津养血', '气虚乏力,食少便溏,中气下陷,久泻脱肛,便血崩漏,表虚自汗,气虚水肿,内热消渴,血虚萎黄', '煎服', '9-30g', '表实邪盛,气滞湿阻,食积停滞等实证,以及阴虚阳亢者,均须禁服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.45, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '红芪';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('黑芝麻', '胡麻、巨胜', '补虚药', '平', '甘', '归肝、肾、大肠经', '补肝肾,益精血,润肠燥', '头晕眼花,耳鸣耳聋,须发早白,病后脱发,肠燥便秘', '煎服', '9-15g', '大便溏泄者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '黑芝麻';

-- ======================== 收涩药（5 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('五倍子', '文蛤、百虫仓', '收涩药', '寒', '酸、涩', '归肺、大肠、肾经', '敛肺降火,涩肠止泻,敛汗,固精止遗,止血', '肺虚久咳,肺热痰嗽,久泻久痢,自汗盗汗,遗精滑精,崩漏下血,便血痔血', '煎服', '3-6g', '外感风寒或肺有实热者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '五倍子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('罂粟壳', '米壳、御米壳', '收涩药', '平', '酸、涩', '归肺、大肠、肾经', '敛肺,涩肠,止痛', '肺虚久咳,久泻久痢,心腹筋骨诸痛', '煎服', '3-6g', '本品易成瘾,不宜常服,孕妇禁服,咳嗽泻痢初起者忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.40, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '罂粟壳';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('石榴皮', '安石榴皮、酸榴皮', '收涩药', '温', '酸、涩', '归大肠经', '涩肠止泻,止血,驱虫', '久泻久痢,便血崩漏,虫积腹痛', '煎服', '3-9g', '泻痢初起者忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '石榴皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('肉豆蔻', '肉果、玉果', '收涩药', '温', '辛', '归脾、胃、大肠经', '温中行气,涩肠止泻', '脾胃虚寒,久泻不止,脘腹胀痛,食少呕吐', '煎服', '3-9g', '湿热泻痢者忌服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.45, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '肉豆蔻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('诃子', '诃黎勒、随风子', '收涩药', '平', '苦、酸、涩', '归肺、大肠经', '涩肠止泻,敛肺止咳,降火利咽', '久泻久痢,便血脱肛,肺虚喘咳,久嗽不止,咽痛音哑', '煎服', '3-9g', '外邪未解,内有湿热积滞者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '诃子';

-- ======================== 攻毒杀虫止痒药（6 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('硫黄', '石硫黄、黄牙', '攻毒杀虫止痒药', '温', '酸', '归肾、大肠经', '外用解毒杀虫疗疮,内服补火助阳通便', '外治疥癣,湿疹,阴疽疮疡,内服用于阳痿足冷,虚喘冷哮,虚寒便秘', '入丸散', '1.5-3g', '本品有毒,孕妇忌服,阴虚火旺者慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '硫黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('雄黄', '明雄黄、黄金石', '攻毒杀虫止痒药', '温', '辛', '归肝、大肠经', '解毒杀虫,燥湿祛痰,截疟', '痈肿疔疮,湿疹疥癣,蛇虫咬伤,虫积腹痛,惊痫,疟疾', '入丸散', '0.05-0.1g', '本品有毒,内服宜慎,孕妇禁服,切忌火煅', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '雄黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蛇床子', '蛇米、蛇粟', '攻毒杀虫止痒药', '温', '辛、苦', '归肾经', '温肾壮阳,燥湿祛风,杀虫止痒', '阳痿宫冷,寒湿带下,湿痹腰痛,阴部湿痒,湿疹,疥癣', '煎服', '3-9g', '阴虚火旺者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '蛇床子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('土荆皮', '土槿皮、荆树皮', '攻毒杀虫止痒药', '温', '辛', '归肺、脾经', '杀虫止痒', '体癣,手足癣,头癣,湿疹,皮炎', '外用', '适量', '本品有毒,仅供外用,不可内服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '土荆皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白矾', '明矾、矾石', '攻毒杀虫止痒药', '寒', '酸、涩', '归肺、脾、肝、大肠经', '外用解毒杀虫燥湿止痒,内服止血止泻清热消痰', '外治湿疹,疥癣,聤耳流脓,内服用于久泻不止,便血崩漏,痰热壅盛', '入丸散', '0.6-1.5g', '体虚胃弱者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.10, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '白矾';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蟾酥', '蟾酥眉、蛤蟆酥', '攻毒杀虫止痒药', '温', '辛', '归心经', '解毒止痛,开窍醒神', '痈疽疔疮,咽喉肿痛,中暑神昏,痧胀腹痛吐泻', '入丸散', '0.015-0.03g', '本品有毒,孕妇忌服,外用不可入目', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 12.00, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '蟾酥';

-- ======================== 拔毒化腐生肌药（4 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('硼砂', '蓬砂、月石', '拔毒化腐生肌药', '凉', '甘、咸', '归肺、胃经', '外用清热解毒,内服清肺化痰', '咽喉肿痛,口舌生疮,目赤翳障,肺热咳嗽痰黄', '入丸散', '1.5-3g', '体虚者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.20, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '硼砂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('炉甘石', '炉先生、甘石', '拔毒化腐生肌药', '平', '甘', '归肝、胃经', '解毒明目退翳,收湿止痒敛疮', '目赤翳障,睑缘湿烂,溃疡不敛,脓水淋漓,湿疹瘙痒', '外用', '适量', '专供外用,不作内服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.12, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '炉甘石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('砒石', '信石、人言', '拔毒化腐生肌药', '大热', '辛', '归肺、肝经', '外用蚀疮去腐杀虫,内服劫痰平喘', '外治溃疡腐肉不脱,疥癣瘰疬,牙疳痔疮,内服用于寒痰哮喘', '入丸散', '0.002-0.004g', '本品大毒,内服极慎,孕妇禁服,不可久服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 5.00, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '砒石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('铅丹', '黄丹、广丹', '拔毒化腐生肌药', '微寒', '辛', '归心、肝经', '拔毒生肌,杀虫止痒', '外治疮疡溃烂,湿疹瘙痒,疥癣,梅毒', '外用', '适量', '本品有毒,不可内服,误服可致铅中毒', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.25, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '铅丹';

-- ======================== 其他常用（7 味） ========================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('八角茴香', '大茴香、八角', '温里药', '温', '辛', '归肝、肾、脾、胃经', '温阳散寒,理气止痛', '寒疝腹痛,肾虚腰痛,胃寒呕吐,脘腹冷痛', '煎服', '3-6g', '阴虚火旺者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.08, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '八角茴香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蜂房', '露蜂房、马蜂窝', '攻毒杀虫止痒药', '平', '甘', '归胃经', '祛风止痛,攻毒杀虫,消肿', '龋齿牙痛,风湿痹痛,瘰疬,疮疡肿毒,乳痈,疥癣,瘾疹瘙痒', '煎服', '3-5g', '本品有毒,气血虚弱者慎服,孕妇慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.45, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '蜂房';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('血竭', '麒麟竭、龙血竭', '活血化瘀药', '平', '甘、咸', '归心、肝经', '活血定痛,化瘀止血,生肌敛疮', '跌扑损伤,瘀血肿痛,外伤出血,疮疡不敛', '入丸散', '0.1-0.3g', '孕妇忌服,无瘀血者慎用', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 4.50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '血竭';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('松花粉', '松花、松黄', '止血药', '温', '甘', '归肝、脾经', '收敛止血,燥湿敛疮', '外伤出血,湿疹,黄水疮,皮肤糜烂,脓水淋漓', '煎服', '3-6g', '无特殊禁忌', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '松花粉';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('枫香脂', '白胶香、枫脂', '活血化瘀药', '平', '辛、微苦', '归肺、脾经', '活血止痛,解毒生肌,凉血', '跌扑损伤,痈疽肿痛,吐血衄血,瘰疬,牙痛', '煎服', '1.5-3g', '孕妇慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.40, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '枫香脂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('木贼', '锉草、节节草', '解表药', '平', '甘、苦', '归肺、肝经', '疏散风热,明目退翳', '风热目赤,目生翳膜,迎风流泪,肠风下血', '煎服', '3-9g', '气血虚者慎服', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.15, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '木贼';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('糯稻根', '稻根须、糯谷根', '收涩药', '平', '甘', '归心、肝经', '敛汗退热,益胃生津', '自汗盗汗,虚热不退,骨蒸劳热', '煎服', '15-30g', '无特殊禁忌', '扩充入库', '2026-07-17 00:00:00', '2026-07-17 00:00:00');
INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 0.06, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00' FROM medicines WHERE name = '糯稻根';
