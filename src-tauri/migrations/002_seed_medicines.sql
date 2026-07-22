-- =====================================================================
-- 002_seed_medicines.sql
-- 中药材销售管理系统 - 内置 300 味常用中药材种子数据
-- 数据来源：d:\learn\trae\python_app\medicines_data_300.py
-- 生成时间：2026-07-19
-- 库存初始化：quantity=1000, unit='g', price=30+(i*7)%170 (30-200 范围), min_stock=100
-- 时间戳：created_at/updated_at 统一使用 '2026-07-17 00:00:00'
-- 使用 INSERT OR IGNORE 避免与 001_init.sql 中已有数据冲突
-- 每味药材对应 2 条 SQL：medicines INSERT + inventory INSERT...SELECT
-- =====================================================================

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('人参', '黄参、地精、神草', '补虚药', '温', '甘、微苦', '归脾、肺、心经', '大补元气，复脉固脱，补脾益肺，生津，安神', '体虚欲脱，肢冷脉微,脾虚食少,肺虚喘咳,津伤口渴,内热消渴,久病虚羸,惊悸失眠,阳痿宫冷', '煎服', '3-9g', '实证、热证而正气不虚者忌服', '一等选装人参', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '人参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('黄芪', '黄耆', '补虚药', '微温', '甘', '归脾、肺经', '补气升阳，固表止汗,利水消肿,生津养血,行滞通痹,托毒排脓,敛疮生肌', '气虚乏力,食少便溏,中气下陷,久泻脱肛,便血崩漏,表虚自汗,气虚水肿,内热消渴,血虚萎黄,半身不遂,痹痛麻木,痈疽难溃,久溃不敛', '煎服', '9-30g', '表实邪盛,气滞湿阻,食积停滞,痈疽初起或溃后热毒尚盛等实证,以及阴虚阳亢者,均须禁服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 37, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '黄芪';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('当归', '干归', '补虚药', '温', '甘、辛', '归肝、心、脾经', '补血活血,调经止痛,润肠通便', '血虚萎黄,眩晕心悸,月经不调,经闭痛经,虚寒腹痛,风湿痹痛,跌扑损伤,痈疽疮疡,肠燥便秘', '煎服', '6-12g', '湿阻中满及大便溏泄者慎服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 44, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '当归';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白芍', '白芍药', '补虚药', '微寒', '苦、酸', '归肝、脾经', '养血调经,敛阴止汗,柔肝止痛', '血虚萎黄,月经不调,崩漏,自汗,盗汗,头痛眩晕,胁痛腹痛,四肢挛急,面色苍白', '煎服', '6-15g', '阳衰虚寒之证不宜用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 51, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白芍';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('熟地黄', '熟地', '补虚药', '微温', '甘', '归肝、肾经', '补血滋阴,益精填髓', '血虚萎黄,眩晕心悸,月经不调,崩漏,肾虚喘咳,须发早白,消渴,便秘,肾虚腰痛', '煎服', '9-30g', '脾虚湿滞,腹满便溏,痰多者不宜使用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 58, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '熟地黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('党参', '上党参、中灵参', '补虚药', '平', '甘', '归脾、肺经', '补中益气,健脾益肺,养血生津', '脾肺气虚,食少便溏,四肢乏力,气血两亏,久泻脱肛,血虚萎黄', '煎服', '9-30g', '不宜与藜芦同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 65, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '党参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白术', '于术、浙术', '补虚药', '温', '苦、甘', '归脾、胃经', '健脾益气,燥湿利水,止汗,安胎', '脾虚食少,腹胀泄泻,痰饮眩悸,水肿,自汗,胎动不安', '煎服', '6-12g', '阴虚内热,津枯液燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 72, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白术';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('茯苓', '云苓、松苓', '利水渗湿药', '平', '甘、淡', '归心、脾、肾经', '利水渗湿,健脾宁心', '水肿尿少,痰饮眩悸,脾虚食少,便溏泄泻,心神不安,惊悸失眠', '煎服', '10-15g', '阴虚而无湿热者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 79, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '茯苓';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('甘草', '国老、甜草', '补虚药', '平', '甘', '归心、肺、脾、胃经', '补脾益气,清热解毒,祛痰止咳,缓急止痛', '脾胃虚弱,倦怠乏力,心悸气短,咳嗽痰多,脘腹四肢挛急疼痛,痈肿疮毒', '煎服', '2-10g', '不宜与京大戟、芫花、甘遂同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 86, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '甘草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('金银花', '忍冬花、银花、双花', '清热药', '寒', '甘', '归肺、心、胃经', '清热解毒,疏散风热', '痈肿疔疮,喉痹,丹毒,热毒血痢,风热感冒,温病发热', '煎服', '6-15g', '脾胃虚寒及气虚疮疡脓清者不宜使用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 93, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '金银花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('连翘', '连壳、黄花条', '清热药', '微寒', '苦', '归肺、心、小肠经', '清热解毒,消肿散结,疏散风热', '痈疽,瘰疬,乳痈,丹毒,风热感冒,温病初起,热入营血,高热烦渴', '煎服', '6-15g', '脾胃虚寒及气虚脓清者不宜使用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 100, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '连翘';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('板蓝根', '大青根、蓝靛根', '清热药', '寒', '苦', '归心、胃经', '清热解毒,凉血利咽', '温毒发斑,舌绛紫暗,烂喉丹痄,大头瘟疫', '煎服', '9-15g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 107, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '板蓝根';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蒲公英', '黄花地丁、婆婆丁', '清热药', '寒', '苦、甘', '归肝、胃经', '清热解毒,消肿散结,利尿通淋', '疔疮肿毒,乳痈,肺痈,肠痈,湿热黄疸,热淋涩痛', '煎服', '10-30g', '用量过大可致缓泻', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 114, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蒲公英';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('黄芩', '条芩、子芩', '清热药', '寒', '苦', '归肺、胆、脾、大肠经', '清热燥湿,泻火解毒,止血安胎', '湿温、暑湿,胸闷呕恶,湿热痞满,泻痢,黄疸,肺热咳嗽,高热烦渴,血热吐衄,胎动不安', '煎服', '3-10g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 121, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '黄芩';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('黄连', '川连、味连', '清热药', '寒', '苦', '归心、脾、胃、肝、胆、大肠经', '清热燥湿,泻火解毒', '湿热痞满,呕吐吞酸,泻痢,黄疸,高热神昏,心火亢盛,心烦不寐,血热吐衄,目赤牙痛,消渴,痈肿疔疮', '煎服', '2-5g', '脾胃虚寒者慎用,阴虚津伤者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 128, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '黄连';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('黄柏', '川柏、关黄柏', '清热药', '寒', '苦', '归肾、膀胱经', '清热燥湿,泻火除蒸,解毒疗疮', '湿热泻痢,黄疸,带下,热淋,脚气,痿软,盗汗,遗精,疮疡肿毒,湿疹瘙痒', '煎服', '3-12g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 135, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '黄柏';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('麻黄', '龙沙、狗骨', '解表药', '温', '辛、微苦', '归肺、膀胱经', '发汗解表,宣肺平喘,利水消肿', '风寒感冒,胸闷喘咳,风水浮肿,支气管哮喘', '煎服', '2-9g', '体虚自汗,盗汗,虚喘者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 142, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '麻黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桂枝', '柳桂', '解表药', '温', '辛、甘', '归心、肺、膀胱经', '发汗解肌,温通经脉,助阳化气,平冲降逆', '风寒感冒,脘腹冷痛,血寒经闭,关节痹痛,痰饮水肿,心悸', '煎服', '3-10g', '热病高热,阴虚火旺,血热妄行者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 149, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桂枝';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('柴胡', '茈胡、北柴胡', '解表药', '微寒', '苦、辛', '归肝、胆经', '疏散退热,疏肝解郁,升举阳气', '感冒发热,寒热往来,胸胁胀痛,月经不调,子宫脱垂,脱肛', '煎服', '3-10g', '肝阳上亢,气机上逆者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 156, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '柴胡';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('川芎', '芎藭', '活血化瘀药', '温', '辛', '归肝、胆、心包经', '活血行气,祛风止痛', '月经不调,经闭痛经,产后瘀滞腹痛,胸胁刺痛,跌扑损伤,头痛,风湿痹痛', '煎服', '3-10g', '阴虚火旺,上盛下虚及气弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 163, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '川芎';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('丹参', '红参、血参', '活血化瘀药', '微寒', '苦', '归心、心包、肝经', '活血祛瘀,通经止痛,清心除烦,凉血消痈', '月经不调,经闭痛经,胸腹刺痛,热痹疼痛,疮疡肿痛,心烦不眠', '煎服', '5-15g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 170, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '丹参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('红花', '红蓝花、刺红花', '活血化瘀药', '温', '辛', '归心、肝经', '活血通经,祛瘀止痛', '经闭,痛经,恶露不行,胸痹心痛,瘀滞腹痛,跌打损伤,疮疡肿痛', '煎服', '3-10g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 177, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '红花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桃仁', '桃核仁', '活血化瘀药', '平', '苦、甘', '归心、肝、大肠经', '活血祛瘀,润肠通便', '经闭痛经,癥瘕痞块,跌打损伤,肠燥便秘', '煎服', '5-10g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 184, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桃仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('半夏', '三叶半夏、三步跳', '化痰止咳平喘药', '温', '辛', '归脾、胃、肺经', '燥湿化痰,降逆止呕', '湿痰寒痰,咳喘痰多,痰饮眩悸,风痰眩晕,痰厥头痛,呕吐反胃', '煎服', '3-9g', '阴虚燥咳,津伤口渴,血证者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 191, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '半夏';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('陈皮', '橘皮、广陈皮', '理气药', '温', '苦、辛', '归脾、肺经', '理气健脾,燥湿化痰', '胸脘胀满,食少吐泻,咳嗽痰多', '煎服', '3-10g', '气虚体燥,阴虚燥咳者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 198, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '陈皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('枳实', '酸橙子、枳壳', '理气药', '微寒', '苦、辛', '归脾、胃、大肠经', '破气消积,化痰散痞', '积滞内停,痞满胀痛,泻痢后重,大便不通,痰滞胸脘,胸痹', '煎服', '3-10g', '脾胃虚弱及孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '枳实';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('山楂', '山里红果、红果', '消食药', '微温', '酸、甘', '归脾、胃、肝经', '消食健胃,行气散瘀', '肉食积滞,胃脘胀满,泻痢腹痛,瘀血经闭,产后瘀阻,心腹刺痛', '煎服', '10-15g', '脾胃虚弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 42, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '山楂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('神曲', '六神曲、建曲', '消食药', '温', '甘、辛', '归脾、胃经', '消食化积,健脾和胃', '饮食停滞,消化不良,胸痞腹胀,呕吐泻痢', '煎服', '6-15g', '脾阴虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 49, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '神曲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('麦芽', '大麦芽、麦糵', '消食药', '平', '甘', '归脾、胃经', '消食健胃,回乳消胀', '食积不消,脘腹胀痛,脾虚食少,乳汁郁积,乳房胀痛', '煎服', '10-15g', '哺乳期妇女慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 56, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '麦芽';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('酸枣仁', '枣仁、酸枣核', '安神药', '平', '甘、酸', '归心、肝、胆经', '养心补肝,宁心安神,敛汗', '虚烦不眠,惊悸多梦,体虚多汗', '煎服', '9-15g', '实邪郁火者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 63, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '酸枣仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('柏子仁', '柏实、侧柏子', '安神药', '平', '甘', '归心、肾、大肠经', '养心安神,润肠通便', '虚烦失眠,心悸怔忡,阴伤便秘', '煎服', '3-9g', '便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 70, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '柏子仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('远志', '小草、细草', '安神药', '温', '苦、辛', '归心、肾、肺经', '安神益智,祛痰消肿', '心肾不交,失眠多梦,健忘惊悸,咳痰不爽,疮疡肿毒', '煎服', '3-9g', '胃炎及胃溃疡者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 77, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '远志';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('天麻', '赤箭、定风草', '平肝息风药', '平', '甘', '归肝经', '息风止痉,平抑肝阳,祛风通络', '肝风内动,眩晕头痛,肢体麻木,手足不遂,风湿痹痛', '煎服', '3-9g', '气血虚甚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 84, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '天麻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('钩藤', '勾藤、双钩藤', '平肝息风药', '微寒', '甘', '归肝、心包经', '清热平肝,息风止痉', '肝火上炎,头痛眩晕,肝风内动,惊痫抽搐,妊娠子痫', '煎服', '3-12g', '无特殊禁忌', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 91, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '钩藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('石决明', '鲍鱼壳、九孔石决明', '平肝息风药', '寒', '咸', '归肝经', '平肝潜阳,清肝明目', '肝阳上亢,头晕目眩,目赤肿痛,视物昏花', '煎服', '3-15g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 98, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '石决明';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('牡蛎', '左牡蛎、海蛎子壳', '平肝息风药', '微寒', '咸、涩', '归肝、胆、肾经', '重镇安神,潜阳补阴,软坚散结', '惊悸失眠,眩晕耳鸣,瘰疬痰核,徵瘕痞块', '煎服', '9-30g', '体虚有寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 105, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '牡蛎';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('龙骨', '白龙骨、五花龙骨', '安神药', '平', '甘、涩', '归心、肝、肾经', '镇惊安神,敛汗固精,止血涩肠', '心悸怔忡,失眠健忘,惊痫癫狂,自汗盗汗,遗精淋浊,崩漏', '煎服', '15-30g', '湿热积滞者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 112, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '龙骨';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('朱砂', '辰砂、丹砂', '安神药', '微寒', '甘', '归心经', '清心镇惊,安神解毒', '心悸易惊,失眠多梦,癫痫发狂,小儿惊风,疮疡肿毒', '入丸散', '0.1-0.5g', '不宜久服,肝肾功能不全者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 119, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '朱砂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('磁石', '吸铁石、慈石', '安神药', '寒', '咸', '归心、肝、肾经', '镇惊安神,平肝潜阳,聪耳明目', '心悸失眠,头晕目眩,惊痫癫狂,耳鸣耳聋,视物昏花', '煎服', '9-30g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 126, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '磁石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('琥珀', '血珀、红琥珀', '安神药', '平', '甘', '归心、肝、膀胱经', '镇惊安神,活血散瘀,利尿通淋', '惊悸失眠,惊风癫痫,瘀血阻滞,淋证癃闭', '研末冲服', '1.5-3g', '阴虚内热者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 133, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '琥珀';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('灵芝', '赤芝、红芝', '安神药', '平', '甘', '归心、肺、肝、肾经', '补气安神,止咳平喘', '心神不宁,失眠心悸,肺虚咳喘,虚劳短气', '煎服', '6-12g', '实证者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 140, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '灵芝';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('合欢皮', '合昏、夜合皮', '安神药', '平', '甘', '归心、肝经', '解郁安神,活血消肿', '心神不宁,忧郁失眠,肺痈疮肿,跌打损伤', '煎服', '6-12g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 147, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '合欢皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('夜交藤', '首乌藤、何首乌藤', '安神药', '平', '甘', '归心、肝经', '养心安神,祛风通络', '失眠多梦,血虚身痛,风湿痹痛,皮肤瘙痒', '煎服', '9-15g', '大便溏泄者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 154, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '夜交藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('人参叶', '参叶', '补虚药', '寒', '苦、甘', '归肺、胃经', '补气益肺,祛暑生津', '气虚咳嗽,暑热烦躁,津伤口渴', '煎服', '3-9g', '实证、热证者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 161, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '人参叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('西洋参', '花旗参、洋参', '补虚药', '凉', '苦、微甘', '归心、肺、肾经', '补气养阴,清热生津', '气虚阴亏,虚热烦倦,咳喘痰血,内热消渴', '另煎兑服', '3-6g', '中阳衰微,胃有寒湿者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 168, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '西洋参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('太子参', '孩儿参、童参', '补虚药', '平', '甘、微苦', '归脾、肺经', '益气健脾,生津润肺', '脾虚体倦,食欲不振,病后虚弱,阴虚盗汗', '煎服', '9-30g', '实证者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 175, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '太子参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('山药', '怀山药、淮山', '补虚药', '平', '甘', '归脾、肺、肾经', '补脾养胃,生津益肺,补肾涩精', '脾虚食少,久泻不止,肺虚喘咳,肾虚遗精,带下尿频', '煎服', '15-30g', '湿盛中满者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 182, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '山药';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白扁豆', '扁豆、眉豆', '补虚药', '微温', '甘', '归脾、胃经', '健脾化湿,和中消暑', '脾胃虚弱,食欲不振,大便溏泻,白带过多,暑湿吐泻', '煎服', '9-15g', '无特殊禁忌', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 189, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白扁豆';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('大枣', '红枣、干枣', '补虚药', '温', '甘', '归脾、胃、心经', '补中益气,养血安神', '脾虚食少,乏力便溏,妇人脏躁', '煎服', '6-15g', '湿盛脘腹胀满者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 196, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '大枣';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('刺五加', '刺拐棒、老虎镣', '补虚药', '温', '辛、微苦', '归脾、肾、心经', '益气健脾,补肾安神', '脾肺气虚,体虚乏力,食欲不振,肾虚腰膝酸软,失眠多梦', '煎服', '9-30g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 33, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '刺五加';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('绞股蓝', '七叶胆、小苦药', '补虚药', '寒', '苦', '归肺、脾、肾经', '清热解毒,止咳祛痰,补气养阴', '气虚阴亏,肺热咳嗽,痰多黄稠,慢性气管炎', '煎服', '6-15g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 40, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '绞股蓝';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('红景天', '蔷薇红景天', '补虚药', '寒', '甘、涩', '归肺、心经', '益气活血,通脉平喘', '气虚血瘀,胸痹心痛,中风偏瘫,倦怠气喘', '煎服', '3-6g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 47, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '红景天';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('沙棘', '沙枣、醋柳果', '补虚药', '温', '酸、涩', '归脾、胃、肺、心经', '健脾消食,止咳祛痰,活血散瘀', '脾虚食少,食积腹痛,咳嗽痰多,胸痹心痛,跌打损伤', '煎服', '3-9g', '体温热甚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 54, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '沙棘';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蜂蜜', '蜜糖、蜂糖', '补虚药', '平', '甘', '归肺、脾、大肠经', '补中润燥,止痛解毒', '脘腹疼痛,肺燥咳嗽,肠燥便秘,目赤口疮,溃疡不敛', '冲服', '15-30g', '湿阻中满,湿热痰滞者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 61, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蜂蜜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鹿茸', '斑龙珠', '补虚药', '温', '甘、咸', '归肾、肝经', '壮肾阳,益精血,强筋骨,调冲任', '肾阳不足,阳痿滑精,宫冷不孕,羸瘦神疲,畏寒眩晕,耳鸣耳聋,腰脊冷痛', '研末冲服', '1-2g', '阴虚阳亢,血分有热,胃火盛者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 68, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鹿茸';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫河车', '胎盘、人胞', '补虚药', '温', '甘、咸', '归肺、肝、肾经', '温肾补精,益气养血', '虚劳羸瘦,骨蒸盗汗,咳嗽气喘,食少气短,阳痿遗精,不孕少乳', '研末冲服', '2-3g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 75, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '紫河车';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('淫羊藿', '仙灵脾', '补虚药', '温', '辛、甘', '归肝、肾经', '补肾阳,强筋骨,祛风湿', '肾阳虚衰,阳痿遗精,筋骨痿软,风湿痹痛,麻木拘挛', '煎服', '6-10g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 82, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '淫羊藿';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('巴戟天', '巴戟、鸡肠风', '补虚药', '微温', '辛、甘', '归肾、肝经', '补肾阳,强筋骨,祛风湿', '阳痿遗精,宫冷不孕,月经不调,少腹冷痛,风湿痹痛', '煎服', '6-15g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 89, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '巴戟天';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('仙茅', '独茅根、地棕根', '补虚药', '热', '辛', '归肾、肝经', '补肾阳,强筋骨,祛寒湿', '阳痿精冷,筋骨痿软,腰膝冷痛,阳虚冷泻', '煎服', '3-9g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 96, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '仙茅';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('杜仲', '思仙、木绵', '补虚药', '温', '甘', '归肝、肾经', '补肝肾,强筋骨,安胎', '肾虚腰痛,筋骨无力,妊娠漏血,胎动不安,高血压', '煎服', '6-10g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 103, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '杜仲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('续断', '川断、接骨草', '补虚药', '微温', '苦、辛', '归肝、肾经', '补肝肾,强筋骨,续折伤,止崩漏', '腰膝酸软,风湿痹痛,跌打损伤,崩漏下血,胎动不安', '煎服', '9-15g', '痢疾初起者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 110, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '续断';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('肉苁蓉', '大芸、寸芸', '补虚药', '温', '甘、咸', '归肾、大肠经', '补肾阳,益精血,润肠通便', '阳痿不孕,腰膝酸软,筋骨无力,肠燥便秘', '煎服', '6-10g', '阴虚火旺,大便溏泄者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 117, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '肉苁蓉';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('锁阳', '琐阳、不老药', '补虚药', '温', '甘', '归肝、肾、大肠经', '补肾阳,益精血,润肠通便', '肾阳不足,精血亏虚,腰膝痿软,肠燥便秘', '煎服', '5-10g', '阴虚火旺,脾虚泄泻者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 124, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '锁阳';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('补骨脂', '破故纸、故子', '补虚药', '温', '辛、苦', '归肾、脾经', '补肾壮阳,固精缩尿,温脾止泻', '肾阳不足,阳痿遗精,遗尿尿频,腰膝冷痛,肾虚作喘,五更泄泻', '煎服', '6-10g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 131, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '补骨脂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('益智仁', '益智子', '补虚药', '温', '辛', '归肾、脾经', '温肾固精缩尿,温脾开胃摄唾', '肾虚遗尿,小便频数,遗精白浊,脾胃虚寒,腹痛吐泻,口涎自流', '煎服', '3-10g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 138, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '益智仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('菟丝子', '菟丝实、吐丝子', '补虚药', '平', '辛、甘', '归肝、肾、脾经', '补肾益精,养肝明目,固精缩尿,止泻安胎', '腰膝酸痛,阳痿遗精,遗尿尿频,目昏耳鸣,脾肾虚泻,胎动不安', '煎服', '6-12g', '阴虚火旺,大便燥结者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 145, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '菟丝子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('沙苑子', '沙苑蒺藜、潼蒺藜', '补虚药', '温', '甘', '归肝、肾经', '补肾固精,养肝明目', '肾虚腰痛,阳痿遗精,遗尿尿频,白带过多,目暗不明', '煎服', '9-15g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 152, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '沙苑子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蛤蚧', '大壁虎、仙蟾', '补虚药', '平', '咸', '归肺、肾经', '补肺益肾,纳气定喘,助阳益精', '虚喘气促,劳嗽咳血,阳痿遗精', '煎服或研末', '3-6g', '风寒咳嗽者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 159, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蛤蚧';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('核桃仁', '胡桃仁、核桃肉', '补虚药', '温', '甘', '归肾、肺、大肠经', '补肾温肺,润肠通便', '肾阳不足,腰膝酸软,阳痿遗精,肺虚咳嗽,肠燥便秘', '煎服', '10-30g', '阴虚火旺,痰热咳嗽者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 166, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '核桃仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('冬虫夏草', '虫草、夏草冬虫', '补虚药', '平', '甘', '归肺、肾经', '补肾益肺,止血化痰', '肾虚阳痿,腰膝酸痛,久咳虚喘,劳嗽咯血', '煎服或研末', '3-9g', '有表邪者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 173, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '冬虫夏草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('胡芦巴', '芦巴子、香草', '补虚药', '温', '苦', '归肾经', '温肾助阳,散寒止痛', '肾脏虚冷,腹胁胀满,寒湿脚气,寒疝腹痛', '煎服', '3-10g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 180, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '胡芦巴';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('韭菜子', '韭子、韭菜仁', '补虚药', '温', '辛、甘', '归肝、肾经', '温补肝肾,壮阳固精', '肾虚阳痿,腰膝酸软,遗精遗尿,小便频数', '煎服', '3-9g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 187, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '韭菜子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('阳起石', '羊起石、白石', '补虚药', '温', '咸', '归肾经', '温肾壮阳', '肾阳虚衰,阳痿宫冷,腰膝冷痹', '煎服', '3-6g', '阴虚火旺者忌用,不宜久服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 194, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '阳起石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫石英', '萤石、氟石', '补虚药', '温', '甘', '归心、肺、肾经', '温肾暖宫,镇心安神,温肺平喘', '肾阳不足,宫冷不孕,惊悸怔忡,虚烦不眠,肺寒咳喘', '煎服', '9-15g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 31, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '紫石英';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('海马', '水马、马头鱼', '补虚药', '温', '甘、咸', '归肝、肾经', '补肾壮阳,调气活血', '肾虚阳痿,遗尿尿频,跌打损伤,疔疮肿毒', '研末冲服', '1-3g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 38, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '海马';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('阿胶', '驴皮胶、傅致胶', '补虚药', '平', '甘', '归肺、肝、肾经', '补血止血,滋阴润燥', '血虚萎黄,眩晕心悸,肌痿无力,吐血衄血,便血崩漏,妊娠胎漏', '烊化兑服', '3-9g', '脾胃虚弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 45, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '阿胶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('何首乌', '首乌、赤首乌', '补虚药', '微温', '苦、甘、涩', '归肝、心、肾经', '补肝肾,益精血,乌须发,强筋骨', '血虚萎黄,眩晕耳鸣,须发早白,腰膝酸软,肢体麻木,崩漏带下', '煎服', '6-12g', '大便溏泄者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 52, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '何首乌';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('龙眼肉', '桂圆肉、益智', '补虚药', '温', '甘', '归心、脾经', '补益心脾,养血安神', '气血不足,心悸怔忡,健忘失眠,血虚萎黄', '煎服', '9-15g', '湿盛中满者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 59, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '龙眼肉';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('楮实子', '构树子、谷实', '补虚药', '寒', '甘', '归肝、肾经', '补肾清肝,明目,利尿', '肝肾不足,腰膝酸软,头晕目昏,水肿胀满', '煎服', '6-12g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 66, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '楮实子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('北沙参', '海沙参、银沙参', '补虚药', '微寒', '甘、微苦', '归肺、胃经', '养阴清肺,益胃生津', '肺热燥咳,劳嗽咯血,热病伤津,咽干口渴', '煎服', '5-12g', '风寒咳嗽者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 73, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '北沙参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('南沙参', '沙参、泡参', '补虚药', '微寒', '甘', '归肺、胃经', '养阴清肺,益胃生津,化痰益气', '肺热燥咳,阴虚劳嗽,干咳痰粘,胃阴不足,气虚乏力', '煎服', '9-15g', '风寒咳嗽者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 80, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '南沙参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('百合', '白百合、蒜脑薯', '补虚药', '微寒', '甘', '归心、肺经', '养阴润肺,清心安神', '阴虚燥咳,劳嗽咯血,虚烦惊悸,失眠多梦,精神恍惚', '煎服', '6-12g', '风寒咳嗽者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 87, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '百合';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('麦冬', '麦门冬、寸冬', '补虚药', '微寒', '甘、微苦', '归心、肺、胃经', '养阴生津,润肺清心', '肺燥干咳,阴虚劳嗽,喉痹咽痛,津伤口渴,内热消渴,心烦失眠', '煎服', '6-12g', '脾胃虚寒泄泻者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 94, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '麦冬';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('天冬', '天门冬、明天冬', '补虚药', '寒', '甘、苦', '归肺、肾经', '养阴润燥,清肺生津', '肺燥干咳,顿咳痰黏,咽干口渴,肠燥便秘', '煎服', '6-12g', '脾胃虚寒泄泻者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 101, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '天冬';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('石斛', '金钗石斛、吊兰花', '补虚药', '微寒', '甘', '归胃、肾经', '益胃生津,滋阴清热', '热病伤津,口干烦渴,胃阴不足,食少干呕,病后虚热不退,阴虚火旺', '煎服', '6-12g', '温热病早期阴未伤者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 108, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '石斛';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('玉竹', '萎蕤、女萎', '补虚药', '微寒', '甘', '归肺、胃经', '养阴润燥,生津止渴', '肺胃阴伤,燥热咳嗽,咽干口渴,内热消渴', '煎服', '6-12g', '痰湿气滞者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 115, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '玉竹';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('黄精', '老虎姜、鸡头参', '补虚药', '平', '甘', '归脾、肺、肾经', '补气养阴,健脾润肺,益肾', '脾胃气虚,体倦乏力,胃阴不足,口干食少,肺虚燥咳,劳嗽咯血,精血不足,腰膝酸软', '煎服', '9-15g', '痰湿气滞者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 122, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '黄精';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('枸杞子', '杞子、枸杞果', '补虚药', '平', '甘', '归肝、肾经', '滋补肝肾,益精明目', '肝肾不足,腰膝酸软,头晕目昏,视力减退,遗精消渴', '煎服', '6-12g', '脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 129, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '枸杞子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('墨旱莲', '旱莲草、鳢肠', '补虚药', '寒', '甘、酸', '归肝、肾经', '滋补肝肾,凉血止血', '肝肾不足,头晕目眩,须发早白,吐血衄血,尿血血痢,崩漏下血', '煎服', '6-12g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 136, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '墨旱莲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('女贞子', '女贞实、冬青子', '补虚药', '凉', '甘、苦', '归肝、肾经', '滋补肝肾,明目乌发', '肝肾不足,眩晕耳鸣,腰膝酸软,须发早白,目暗不明', '煎服', '6-12g', '脾胃虚寒泄泻者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 143, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '女贞子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桑椹', '桑果、桑枣', '补虚药', '寒', '甘、酸', '归心、肝、肾经', '滋阴补血,生津润燥', '肝肾不足,血虚精亏,头晕眼花,须发早白,内热消渴,肠燥便秘', '煎服', '9-15g', '脾胃虚寒便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 150, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桑椹';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('龟甲', '龟板、下甲', '补虚药', '寒', '甘、咸', '归肝、肾、心经', '滋阴潜阳,益肾强骨,养血补心', '阴虚阳亢,眩晕耳鸣,阴虚火旺,骨蒸潮热,盗汗遗精,肾虚腰痛,筋骨痿软,心虚惊悸', '煎服', '9-24g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 157, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '龟甲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鳖甲', '甲鱼壳、团鱼甲', '补虚药', '寒', '咸', '归肝、肾经', '滋阴潜阳,退热除蒸,软坚散结', '阴虚发热,骨蒸劳热,虚风内动,经闭,癥瘕,久疟疟母', '煎服', '9-24g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 164, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鳖甲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('大黄', '将军、川军', '泻下药', '寒', '苦', '归脾、胃、大肠、肝、心包经', '泻下攻积,清热泻火,凉血解毒,逐瘀通经,利湿退黄', '实热积滞便秘,血热吐衄,目赤咽肿,痈肿疔疮,肠痈腹痛,瘀血经闭,产后瘀阻,跌打损伤,湿热痢疾,黄疸尿赤,淋证,水肿；外治烧烫伤', '煎服', '3-15g', '孕妇及月经期、哺乳期慎用', '生大黄', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 171, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '大黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('芒硝', '马牙硝、盆硝', '泻下药', '寒', '咸、苦', '归胃、大肠经', '泻下通便,润燥软坚,清热消肿', '实热便秘,大便燥结,积滞腹痛,肠痈肿痛；外治乳痈,痔疮肿痛', '冲服', '6-12g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 178, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '芒硝';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('番泻叶', '泻叶、旃那叶', '泻下药', '寒', '甘、苦', '归大肠经', '泻热行滞,通便利水', '热结便秘,积滞腹胀', '泡服', '2-6g', '孕妇慎用,用量过大可致恶心呕吐腹痛', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 185, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '番泻叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('芦荟', '卢会、讷会', '泻下药', '寒', '苦', '归肝、胃、大肠经', '泻下通便,清肝泻火,杀虫疗疳', '热结便秘,惊痫抽搐,小儿疳积,外治癣疮', '入丸散', '2-5g', '孕妇慎用,脾胃虚寒者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 192, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '芦荟';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('火麻仁', '麻子仁、大麻仁', '泻下药', '平', '甘', '归脾、胃、大肠经', '润肠通便', '血虚津亏,肠燥便秘', '煎服', '10-15g', '用量过大可致中毒', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 199, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '火麻仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('郁李仁', '李仁、郁子', '泻下药', '平', '辛、苦、甘', '归脾、大肠、小肠经', '润燥滑肠,下气利水', '肠燥便秘,水肿腹满,脚气浮肿', '煎服', '6-10g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 36, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '郁李仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('松子仁', '松子、海松子', '泻下药', '温', '甘', '归肺、肝、大肠经', '润肠通便,润肺止咳', '肠燥便秘,肺燥干咳', '煎服', '5-10g', '脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 43, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '松子仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('甘遂', '甘泽、苦泽', '泻下药', '寒', '苦', '归肺、肾、大肠经', '泻水逐饮,消肿散结', '水肿胀满,胸腹积水,痰饮积聚,气逆喘咳,二便不利', '入丸散', '0.5-1g', '孕妇忌用,体虚者慎用,反甘草', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '甘遂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('京大戟', '大戟、龙虎草', '泻下药', '寒', '苦', '归肺、脾、肾经', '泻水逐饮,消肿散结', '水肿胀满,胸腹积水,痰饮积聚,瘰疬痰核,痈肿疮毒', '煎服', '1.5-3g', '孕妇忌用,体虚者慎用,反甘草', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 57, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '京大戟';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('芫花', '赤芫、杜芫', '泻下药', '温', '苦、辛', '归肺、脾、肾经', '泻水逐饮,祛痰止咳,杀虫疗疮', '水肿胀满,胸腹积水,痰饮积聚,咳嗽痰喘,头疮白秃,顽癣', '煎服', '1.5-3g', '孕妇忌用,体虚者慎用,反甘草', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 64, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '芫花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('商陆', '土人参、山萝卜', '泻下药', '寒', '苦', '归肺、脾、肾、大肠经', '逐水消肿,通利二便,解毒散结', '水肿胀满,二便不利,痈肿疮毒', '煎服', '3-9g', '孕妇忌用,脾虚水肿者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 71, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '商陆';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('牵牛子', '二丑、黑白丑', '泻下药', '寒', '苦', '归肺、肾、大肠经', '泻下逐水,去积杀虫', '水肿胀满,二便不利,痰饮积聚,虫积腹痛', '煎服', '3-6g', '孕妇忌用,胃弱气虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 78, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '牵牛子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('巴豆霜', '巴豆、江子', '泻下药', '热', '辛', '归胃、大肠经', '峻下冷积,逐水退肿,祛痰利咽,外用蚀疮', '寒积便秘,乳食停滞,腹水臌胀,二便不通,喉风喉痹,痈肿脓成未溃,疥癣恶疮', '入丸散', '0.1-0.3g', '孕妇忌用,体弱者慎用,反牵牛子', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 85, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '巴豆霜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('千金子', '续随子、小巴豆', '泻下药', '温', '辛', '归肝、肾、大肠经', '逐水消肿,破血消癥', '水肿,痰饮,积滞胀满,二便不利,血瘀经闭,癥瘕', '去壳去油用', '1-2g', '孕妇忌用,体弱便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 92, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '千金子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('独活', '独摇草、独滑', '祛风湿药', '微温', '辛、苦', '归肾、膀胱经', '祛风除湿,通痹止痛', '风寒湿痹,腰膝疼痛,少阴伏风头痛,风寒挟湿头痛', '煎服', '3-10g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 99, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '独活';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('威灵仙', '铁脚威灵仙、铁扫帚', '祛风湿药', '温', '辛、咸', '归膀胱经', '祛风湿,通经络,消骨鲠', '风湿痹痛,肢体麻木,筋脉拘挛,屈伸不利,骨鲠咽喉', '煎服', '6-10g', '气血亏虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 106, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '威灵仙';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('防己', '粉防己、汉防己', '祛风湿药', '寒', '苦', '归膀胱、肺经', '祛风止痛,利水消肿', '风湿痹痛,水肿脚气,小便不利,湿疹疮毒', '煎服', '5-10g', '胃纳不佳及阴虚体弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 113, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '防己';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('秦艽', '秦胶、秦纠', '祛风湿药', '平', '辛、苦', '归胃、肝、胆经', '祛风湿,清虚热,利湿退黄', '风湿痹痛,筋脉拘挛,骨节烦痛,日晡潮热,小儿疳积发热,湿热黄疸', '煎服', '5-10g', '脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 120, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '秦艽';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('木瓜', '贴梗海棠、铁脚梨', '祛风湿药', '温', '酸', '归肝、脾经', '舒筋活络,和胃化湿', '风湿痹痛,筋脉拘挛,脚气肿痛,吐泻转筋', '煎服', '6-9g', '内有郁热,小便短赤者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 127, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '木瓜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桑寄生', '寄生、广寄生', '祛风湿药', '平', '苦、甘', '归肝、肾经', '祛风湿,补肝肾,强筋骨,安胎元', '风湿痹痛,腰膝酸软,筋骨无力,崩漏经多,妊娠漏血,胎动不安,高血压', '煎服', '10-20g', '无特殊禁忌', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 134, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桑寄生';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('五加皮', '南五加皮、细柱五加', '祛风湿药', '温', '辛、苦', '归肝、肾经', '祛风湿,补肝肾,强筋骨', '风湿痹痛,筋骨痿软,小儿行迟,体虚乏力', '煎服', '5-10g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 141, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '五加皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蕲蛇', '大白花蛇、五步蛇', '祛风湿药', '温', '甘、咸', '归肝经', '祛风通络,止痉止痒', '风湿顽痹,麻木拘挛,中风口眼歪斜,半身不遂,抽搐痉挛,麻风疥癣', '煎服或研末', '3-9g', '血虚生风者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 148, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蕲蛇';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('乌梢蛇', '乌蛇、黑花蛇', '祛风湿药', '平', '甘', '归肝经', '祛风通络,止痉止痒', '风湿顽痹,麻木拘挛,中风口眼歪斜,半身不遂,抽搐痉挛,麻风疥癣,瘰疬恶疮', '煎服或研末', '6-12g', '血虚生风者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 155, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '乌梢蛇';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蛇蜕', '蛇皮、龙衣', '祛风湿药', '平', '咸、甘', '归肝经', '祛风定惊,退翳解毒', '小儿惊风,抽搐痉挛,翳障,喉痹,疔肿,皮肤瘙痒', '煎服或研末', '2-3g', '孕妇忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 162, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蛇蜕';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('苍术', '赤术、青术', '化湿药', '温', '辛、苦', '归脾、胃、肝经', '燥湿健脾,祛风散寒,明目', '湿阻中焦,脘腹胀满,泄泻,水肿,脚气痿躄,风湿痹痛,风寒感冒,夜盲', '煎服', '5-10g', '阴虚内热者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 169, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '苍术';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('厚朴', '川朴、紫油厚朴', '化湿药', '温', '苦、辛', '归脾、胃、肺、大肠经', '燥湿消痰,下气除满', '湿滞伤中,脘痞吐泻,食积气滞,腹胀便秘,痰饮喘咳', '煎服', '3-10g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 176, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '厚朴';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('藿香', '广藿香、枝香', '化湿药', '微温', '辛', '归脾、胃、肺经', '芳香化浊,和中止呕,发表解暑', '湿浊中阻,脘痞呕吐,暑湿表证,湿温初起,发热倦怠,胸闷不舒', '煎服', '5-10g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 183, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '藿香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('佩兰', '兰草、水香', '化湿药', '平', '辛', '归脾、胃、肺经', '芳香化湿,醒脾开胃,发表解暑', '湿浊中阻,脘痞呕恶,口中甜腻,口臭,多涎,暑湿表证,湿温初起', '煎服', '5-10g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 190, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '佩兰';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('砂仁', '缩砂仁、阳春砂', '化湿药', '温', '辛', '归脾、胃、肾经', '化湿开胃,温脾止泻,理气安胎', '湿浊中阻,脘痞不饥,脾胃虚寒,呕吐泄泻,妊娠恶阻,胎动不安', '后下', '3-6g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 197, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '砂仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白豆蔻', '豆蔻、圆豆蔻', '化湿药', '温', '辛', '归肺、脾、胃经', '化湿行气,温中止呕', '湿浊中阻,不思饮食,湿温初起,胸闷不饥,寒湿呕逆,小儿胃寒吐乳', '后下', '3-6g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 34, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白豆蔻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('草豆蔻', '草蔻、偶子', '化湿药', '温', '辛', '归脾、胃经', '燥湿行气,温中止呕', '寒湿内阻,脘腹胀满冷痛,嗳气呕逆,不思饮食', '煎服', '3-6g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 41, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '草豆蔻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('草果', '草果仁、老蔻', '化湿药', '温', '辛', '归脾、胃经', '燥湿温中,除痰截疟', '寒湿内阻,脘腹胀满,痞满呕吐,疟疾寒热,瘟疫发热', '煎服', '3-6g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 48, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '草果';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('泽泻', '水泻、芒芋', '利水渗湿药', '寒', '甘', '归肾、膀胱经', '利水渗湿,泄热,化浊降脂', '小便不利,水肿胀满,泄泻尿少,痰饮眩晕,热淋涩痛,高脂血症', '煎服', '6-10g', '肾虚精滑者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 55, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '泽泻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('薏苡仁', '薏仁、苡仁', '利水渗湿药', '凉', '甘、淡', '归脾、胃、肺经', '利水渗湿,健脾止泻,除痹,排脓,解毒散结', '水肿,脚气,小便不利,脾虚泄泻,湿痹拘挛,肺痈,肠痈,赘疣,癌肿', '煎服', '9-30g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 62, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '薏苡仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('车前子', '车前实、凤眼前仁', '利水渗湿药', '寒', '甘', '归肝、肾、肺、小肠经', '清热利尿通淋,渗湿止泻,明目,祛痰', '热淋涩痛,水肿胀满,暑湿泄泻,目赤肿痛,痰热咳嗽', '包煎', '9-15g', '肾虚精滑者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 69, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '车前子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('滑石', '画石、液石', '利水渗湿药', '寒', '甘、淡', '归膀胱、肺、胃经', '利尿通淋,清热解暑,外用收湿敛疮', '热淋,石淋,尿热涩痛,暑湿烦渴,湿热水泻；外治湿疹,湿疮,痱子', '包煎', '10-20g', '脾虚者慎用,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 76, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '滑石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('木通', '关木通、川木通', '利水渗湿药', '寒', '苦', '归心、小肠、膀胱经', '利尿通淋,清心除烦,通经下乳', '淋证,水肿,心烦尿赤,口舌生疮,经闭乳少,湿热痹痛', '煎服', '3-6g', '孕妇慎用,肾功能不全者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 83, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '木通';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('通草', '大通草、方通草', '利水渗湿药', '微寒', '甘、淡', '归肺、胃经', '清热利尿,通气下乳', '湿热尿赤,淋证涩痛,水肿尿少,乳汁不下', '煎服', '3-5g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 90, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '通草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('瞿麦', '巨句麦、大菊', '利水渗湿药', '寒', '苦', '归心、小肠经', '利尿通淋,破血通经', '热淋,血淋,石淋,小便不通,淋沥涩痛,经闭瘀阻', '煎服', '9-15g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 97, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '瞿麦';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('萹蓄', '萹竹、道生草', '利水渗湿药', '微寒', '苦', '归膀胱经', '利尿通淋,杀虫止痒', '热淋涩痛,小便短赤,虫积腹痛,皮肤湿疹,阴痒带下', '煎服', '9-15g', '脾虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 104, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '萹蓄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('地肤子', '地葵、地麦', '利水渗湿药', '寒', '辛、苦', '归肾、膀胱经', '清热利湿,祛风止痒', '小便涩痛,阴痒带下,风疹,湿疹,皮肤瘙痒', '煎服', '9-15g', '阴虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 111, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '地肤子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('海金沙', '金沙藤、左转藤', '利水渗湿药', '寒', '甘、咸', '归膀胱、小肠经', '清利湿热,通淋止痛', '热淋,石淋,血淋,膏淋,尿道涩痛', '包煎', '6-15g', '肾阴亏虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 118, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '海金沙';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('石韦', '石皮、石剑', '利水渗湿药', '微寒', '甘、苦', '归肺、膀胱经', '利尿通淋,清肺止咳,凉血止血', '热淋,血淋,石淋,小便不通,淋沥涩痛,肺热咳喘,血热出血', '煎服', '6-12g', '阴虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 125, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '石韦';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('冬葵子', '葵子、葵菜子', '利水渗湿药', '寒', '甘', '归大肠、小肠、膀胱经', '利尿通淋,下乳,润肠', '淋证,水肿,乳汁不通,乳房胀痛,肠燥便秘', '煎服', '3-9g', '孕妇慎用,脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 132, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '冬葵子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('灯心草', '灯心、灯草', '利水渗湿药', '微寒', '甘、淡', '归心、肺、小肠经', '清心火,利小便', '心烦失眠,尿少涩痛,口舌生疮', '煎服', '1-3g', '虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 139, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '灯心草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('附子', '黑顺片、白附片', '温里药', '大热', '辛、甘', '归心、肾、脾经', '回阳救逆,补火助阳,散寒止痛', '亡阳虚脱,肢冷脉微,心阳不足,胸痹心痛,虚寒吐泻,脘腹冷痛,肾阳虚衰,阳痿宫冷,阴寒水肿,阳虚外感,寒湿痹痛', '先煎', '3-15g', '孕妇慎用,阴虚阳亢者忌用,反半夏、瓜蒌、贝母、白蔹、白及', '制附子', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 146, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '附子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('干姜', '白姜、均姜', '温里药', '热', '辛', '归脾、胃、肾、心、肺经', '温中散寒,回阳通脉,温肺化饮', '脘腹冷痛,呕吐泄泻,肢冷脉微,寒饮喘咳', '煎服', '3-10g', '阴虚内热,血热妄行者忌用,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 153, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '干姜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('肉桂', '桂皮、牡桂', '温里药', '大热', '辛、甘', '归肾、脾、心、肝经', '补火助阳,引火归元,散寒止痛,温通经脉', '阳痿宫冷,腰膝冷痛,肾虚作喘,眩晕目赤,心腹冷痛,虚寒吐泻,寒疝腹痛,痛经经闭', '后下', '1-5g', '阴虚火旺,里有实热,血热妄行者及孕妇忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 160, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '肉桂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('吴茱萸', '吴萸、左力', '温里药', '热', '辛、苦', '归肝、脾、胃、肾经', '散寒止痛,降逆止呕,助阳止泻', '厥阴头痛,寒疝腹痛,寒湿脚气,经行腹痛,脘腹胀痛,呕吐吞酸,五更泄泻', '煎服', '2-5g', '阴虚有热者忌用,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 167, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '吴茱萸';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('小茴香', '茴香、香丝菜', '温里药', '温', '辛', '归肝、肾、脾、胃经', '散寒止痛,理气和胃', '寒疝腹痛,睾丸偏坠,痛经,少腹冷痛,脘腹胀痛,食少吐泻', '煎服', '3-6g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 174, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '小茴香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('丁香', '公丁香、丁子香', '温里药', '温', '辛', '归脾、胃、肺、肾经', '温中降逆,补肾助阳', '脾胃虚寒,呃逆呕吐,食少吐泻,心腹冷痛,肾虚阳痿', '煎服', '1-3g', '热证及阴虚内热者忌用,畏郁金', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 181, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '丁香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('高良姜', '良姜、小良姜', '温里药', '热', '辛', '归脾、胃经', '温胃止呕,散寒止痛', '脘腹冷痛,胃寒呕吐,嗳气吞酸', '煎服', '3-6g', '阴虚有热者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 188, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '高良姜';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('胡椒', '味履支、玉椒', '温里药', '热', '辛', '归胃、大肠经', '温中散寒,下气消痰', '胃寒呕吐,腹痛泄泻,食欲不振,癫痫痰多', '研粉冲服', '0.6-1.5g', '阴虚有火者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 195, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '胡椒';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('花椒', '川椒、蜀椒', '温里药', '温', '辛', '归脾、胃、肾经', '温中止痛,杀虫止痒', '脘腹冷痛,呕吐泄泻,虫积腹痛,蛔虫症,湿疹瘙痒', '煎服', '3-6g', '阴虚火旺者慎用,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 32, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '花椒';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('荜茇', '荜拨、鼠尾', '温里药', '热', '辛', '归胃、大肠经', '温中散寒,下气止痛', '脘腹冷痛,呕吐吞酸,泄泻痢疾,寒疝腹痛,偏头痛', '煎服', '1-3g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 39, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '荜茇';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('荜澄茄', '澄茄、毕澄茄', '温里药', '温', '辛', '归脾、胃、肾、膀胱经', '温中散寒,行气止痛', '胃寒呕逆,脘腹冷痛,寒疝腹痛,寒湿郁滞,小便浑浊', '煎服', '1-3g', '阴虚火旺者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 46, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '荜澄茄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫苏叶', '苏叶', '解表药', '温', '辛', '归肺、脾经', '解表散寒,行气和胃', '风寒感冒,咳嗽呕恶,妊娠呕吐,鱼蟹中毒', '煎服', '5-9g', '气虚表虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 53, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '紫苏叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('荆芥', '假苏、鼠蓂', '解表药', '微温', '辛', '归肺、肝经', '解表散风,透疹,消疮', '感冒,头痛,麻疹,风疹,疮疡初起', '煎服', '5-10g', '表虚自汗者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 60, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '荆芥';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('防风', '铜芸、屏风', '解表药', '微温', '辛、甘', '归膀胱、肝、脾经', '祛风解表,胜湿止痛,止痉', '感冒头痛,风湿痹痛,风疹瘙痒,破伤风', '煎服', '5-10g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 67, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '防风';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('羌活', '羌青、护羌使者', '解表药', '温', '辛、苦', '归膀胱、肾经', '解表散寒,祛风除湿,止痛', '风寒感冒,头痛项强,风湿痹痛,肩背酸痛', '煎服', '3-9g', '阴虚头痛者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 74, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '羌活';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白芷', '芳香、泽芬', '解表药', '温', '辛', '归肺、胃、大肠经', '解表散寒,祛风止痛,通鼻窍,燥湿止带,消肿排脓', '感冒头痛,眉棱骨痛,鼻塞流涕,鼻渊,牙痛,带下,疮疡肿痛', '煎服', '3-9g', '阴虚血热者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 81, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白芷';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('细辛', '小辛、少辛', '解表药', '温', '辛', '归心、肺、肾经', '解表散寒,祛风止痛,通窍,温肺化饮', '风寒感冒,头痛,牙痛,鼻塞流涕,鼻渊,风湿痹痛,痰饮喘咳', '煎服', '1-3g', '气虚多汗、阴虚阳亢头痛、阴虚燥咳者忌用', '用量不宜过大', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 88, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '细辛';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('藁本', '藁茇、鬼卿', '解表药', '温', '辛', '归膀胱经', '祛风,散寒,除湿,止痛', '风寒感冒,巅顶头痛,风湿痹痛', '煎服', '3-9g', '血虚头痛者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 95, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '藁本';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('苍耳子', '苍耳、葈耳', '解表药', '温', '辛、苦', '归肺经', '散风寒,通鼻窍,祛风湿', '风寒头痛,鼻渊流涕,风疹瘙痒,湿痹拘挛', '煎服', '3-9g', '血虚头痛者不宜用', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 102, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '苍耳子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('辛夷', '木笔花、望春花', '解表药', '温', '辛', '归肺、胃经', '散风寒,通鼻窍', '风寒头痛,鼻塞,鼻渊,鼻流浊涕', '煎服,包煎', '3-9g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 109, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '辛夷';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('葱白', '葱茎白、葱白头', '解表药', '温', '辛', '归肺、胃经', '发汗解表,散寒通阳', '风寒感冒,头痛鼻塞,阴寒腹痛,二便不通,痢疾,痈肿', '煎服', '3-9g', '表虚多汗者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 116, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '葱白';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鹅不食草', '石胡荽、地胡椒', '解表药', '温', '辛', '归肺、肝经', '发散风寒,通鼻窍,止咳', '风寒头痛,咳嗽痰多,鼻塞不通,鼻渊流涕', '煎服', '6-9g', '胃溃疡患者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 123, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鹅不食草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('薄荷', '蕃荷菜、南薄荷', '解表药', '凉', '辛', '归肺、肝经', '疏散风热,清利头目,利咽,透疹,疏肝行气', '风热感冒,风温初起,头痛,目赤,喉痹,口疮,风疹,麻疹,胸胁胀闷', '煎服,后下', '3-6g', '体虚多汗者不宜用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 130, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '薄荷';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('牛蒡子', '恶实、鼠粘子', '解表药', '寒', '辛、苦', '归肺、胃经', '疏散风热,宣肺利咽,解毒透疹,消肿疗疮', '风热感冒,咳嗽痰多,咽喉肿痛,斑疹不透,风疹瘙痒,痈肿疮毒', '煎服', '6-12g', '脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 137, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '牛蒡子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蝉蜕', '蝉衣、蝉壳', '解表药', '寒', '甘', '归肺、肝经', '疏散风热,利咽,透疹止痒,明目退翳,息风止痉', '风热感冒,咽痛音哑,麻疹不透,风疹瘙痒,目赤翳障,惊风抽搐,破伤风', '煎服', '3-6g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 144, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蝉蜕';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桑叶', '铁扇子、蚕叶', '解表药', '寒', '甘、苦', '归肺、肝经', '疏散风热,清肺润燥,平抑肝阳,清肝明目', '风热感冒,肺热燥咳,头晕头痛,目赤昏花', '煎服', '5-9g', '风寒咳嗽者不宜用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 151, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桑叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('菊花', '节华、金精', '解表药', '微寒', '甘、苦', '归肺、肝经', '散风清热,平肝明目,清热解毒', '风热感冒,头痛眩晕,目赤肿痛,眼目昏花,疮痈肿毒', '煎服', '5-9g', '气虚胃寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 158, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '菊花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蔓荆子', '蔓荆实、荆子', '解表药', '微寒', '辛、苦', '归膀胱、肝、胃经', '疏散风热,清利头目', '风热感冒头痛,齿龈肿痛,目赤多泪,目暗不明,头晕目眩', '煎服', '5-9g', '血虚有火之头痛者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 165, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蔓荆子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('升麻', '周升麻、鸡骨升麻', '解表药', '微寒', '辛、甘', '归肺、脾、胃、大肠经', '发表透疹,清热解毒,升举阳气', '风热头痛,齿痛,口疮,咽喉肿痛,麻疹不透,阳毒发斑,脱肛,子宫脱垂', '煎服', '3-9g', '阴虚阳浮,喘满气逆及麻疹已透者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 172, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '升麻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('葛根', '干葛、甘葛', '解表药', '凉', '甘、辛', '归脾、胃、肺经', '解肌退热,生津止渴,透疹,升阳止泻,通经活络,解酒毒', '表证发热,项背强痛,麻疹不透,热病口渴,阴虚消渴,热泻热痢,脾虚泄泻', '煎服', '10-15g', '胃寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 179, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '葛根';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('淡豆豉', '豆豉、香豉', '解表药', '寒', '苦、辛', '归肺、胃经', '解表,除烦,宣发郁热', '感冒,寒热头痛,烦躁胸闷,虚烦不眠', '煎服', '6-12g', '胃虚易泛恶者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 186, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '淡豆豉';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('浮萍', '水萍、萍子草', '解表药', '寒', '辛', '归肺、膀胱经', '宣散风热,透疹止痒,利尿消肿', '风热感冒,麻疹不透,风疹瘙痒,水肿尿少', '煎服', '3-9g', '表虚自汗者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 193, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '浮萍';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('石膏', '细石、软石膏', '清热药', '寒', '甘、辛', '归肺、胃经', '生用清热泻火,除烦止渴;煅用敛疮生肌,收湿,止血', '外感热病,高热烦渴,肺热喘咳,胃火亢盛,头痛,牙痛;煅用治溃疡不敛,湿疹瘙痒,水火烫伤,外伤出血', '煎服,先煎', '15-60g', '脾胃虚寒及阴虚内热者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 30, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '石膏';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('知母', '蚔母、连母', '清热药', '寒', '苦、甘', '归肺、胃、肾经', '清热泻火,滋阴润燥', '外感热病,高热烦渴,肺热燥咳,骨蒸潮热,内热消渴,肠燥便秘', '煎服', '6-12g', '脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 37, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '知母';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('栀子', '黄栀子、山栀', '清热药', '寒', '苦', '归心、肺、三焦经', '泻火除烦,清热利湿,凉血解毒', '热病心烦,湿热黄疸,血淋涩痛,血热吐衄,目赤肿痛,火毒疮疡', '煎服', '6-9g', '脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 44, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '栀子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('夏枯草', '夕句、乃东', '清热药', '寒', '苦、辛', '归肝、胆经', '清热泻火,明目,散结消肿', '目赤肿痛,目珠夜痛,头痛眩晕,瘰疬,瘿瘤,乳痈,乳癖,乳房胀痛', '煎服', '9-15g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 51, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '夏枯草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('芦根', '芦茅根、苇根', '清热药', '寒', '甘', '归肺、胃经', '清热泻火,生津止渴,除烦,止呕,利尿', '热病烦渴,肺热咳嗽,肺痈吐脓,胃热呕哕,热淋涩痛', '煎服', '15-30g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 58, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '芦根';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('天花粉', '栝楼根、瓜蒌根', '清热药', '寒', '甘、微苦', '归肺、胃经', '清热泻火,生津止渴,消肿排脓', '热病烦渴,肺热燥咳,内热消渴,疮疡肿毒', '煎服', '10-15g', '孕妇慎用,不宜与川乌、草乌同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 65, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '天花粉';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('淡竹叶', '竹叶门冬青', '清热药', '寒', '甘、淡', '归心、胃、小肠经', '清热泻火,除烦止渴,利尿通淋', '热病烦渴,口舌生疮,小便短赤,热淋涩痛', '煎服', '6-9g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 72, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '淡竹叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鸭跖草', '鸡舌草、竹叶菜', '清热药', '寒', '甘、淡', '归肺、胃、小肠经', '清热泻火,解毒,利水消肿', '风热感冒,高热不退,咽喉肿痛,水肿尿少,热淋涩痛,痈肿疔毒', '煎服', '15-30g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 79, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鸭跖草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('龙胆', '龙胆草、胆草', '清热药', '寒', '苦', '归肝、胆经', '清热燥湿,泻肝胆火', '湿热黄疸,阴肿阴痒,带下,湿疹瘙痒,肝火目赤,耳鸣耳聋,胁痛口苦,惊风抽搐', '煎服', '3-6g', '脾胃虚寒者忌用,阴虚津伤者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 86, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '龙胆';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('秦皮', '岑皮、秦白皮', '清热药', '寒', '苦、涩', '归肝、胆、大肠经', '清热燥湿,收涩止痢,止带,明目', '湿热泻痢,赤白带下,目赤肿痛,目生翳膜', '煎服', '6-12g', '脾胃虚寒者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 93, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '秦皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('苦参', '苦骨、川参', '清热药', '寒', '苦', '归心、肝、胃、大肠、膀胱经', '清热燥湿,杀虫,利尿', '热痢,便血,黄疸尿闭,赤白带下,阴肿阴痒,湿疹,湿疮,皮肤瘙痒,疥癣麻风', '煎服', '4.5-9g', '脾胃虚寒者忌用,不宜与藜芦同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 100, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '苦参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白鲜皮', '白膻、白羊鲜', '清热药', '寒', '苦', '归脾、胃、膀胱经', '清热燥湿,祛风解毒', '湿热疮毒,黄水淋漓,湿疹,风疹,疥癣疮癞,风湿热痹,黄疸尿赤', '煎服', '5-10g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 107, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白鲜皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫花地丁', '堇菜地丁、紫地丁', '清热药', '寒', '苦、辛', '归心、肝经', '清热解毒,凉血消肿', '疔疮肿毒,痈疽发背,丹毒,毒蛇咬伤', '煎服', '15-30g', '体质虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 114, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '紫花地丁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('野菊花', '山菊花、野黄菊', '清热药', '微寒', '苦、辛', '归肝、心经', '清热解毒,泻火平肝', '疔疮痈肿,目赤肿痛,头痛眩晕', '煎服', '9-15g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 121, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '野菊花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('穿心莲', '一见喜、苦草', '清热药', '寒', '苦', '归心、肺、大肠、膀胱经', '清热解毒,凉血消肿,燥湿', '感冒发热,咽喉肿痛,口舌生疮,顿咳劳嗽,泄泻痢疾,热淋涩痛,痈肿疮疡,毒蛇咬伤', '煎服', '6-9g', '不宜多服久服,脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 128, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '穿心莲';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('大青叶', '蓝叶、蓝菜', '清热药', '寒', '苦', '归心、胃经', '清热解毒,凉血消斑', '温病高热,神昏,发斑发疹,痄腮,喉痹,丹毒,痈肿', '煎服', '9-15g', '脾胃虚寒者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 135, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '大青叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('青黛', '靛花、青蛤粉', '清热药', '寒', '咸', '归肝经', '清热解毒,凉血消斑,泻火定惊', '温毒发斑,血热吐衄,胸痛咳血,口疮,痄腮,喉痹,小儿惊痫', '入丸散,1.5-3g', '1.5-3g', '胃寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 142, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '青黛';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('贯众', '贯仲、绵马贯众', '清热药', '微寒', '苦', '归肝、脾经', '清热解毒,驱虫,止血', '虫积腹痛,疮疡,崩漏,流感,麻疹,流行性腮腺炎', '煎服', '4.5-9g', '孕妇慎用', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 149, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '贯众';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鱼腥草', '蕺菜、折耳根', '清热药', '微寒', '辛', '归肺经', '清热解毒,消痈排脓,利尿通淋', '肺痈吐脓,痰热喘咳,热痢,热淋,痈肿疮毒', '煎服', '15-25g', '虚寒证及阴性疮疡忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 156, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鱼腥草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('射干', '乌扇、扁竹', '清热药', '寒', '苦', '归肺经', '清热解毒,消痰,利咽', '热毒痰火郁结,咽喉肿痛,痰涎壅盛,咳嗽气喘', '煎服', '3-9g', '脾虚便溏者慎用,孕妇忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 163, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '射干';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('山豆根', '广豆根、苦豆根', '清热药', '寒', '苦', '归肺、胃经', '清热解毒,利咽消肿', '火毒蕴结,乳蛾喉痹,咽喉肿痛,齿龈肿痛,口舌生疮', '煎服', '3-6g', '脾胃虚寒泄泻者忌用', '有毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 170, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '山豆根';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('马勃', '马屁勃、马屁包', '清热药', '平', '辛', '归肺经', '清肺利咽,止血', '风热郁肺咽痛,音哑,咳嗽,外治鼻衄,创伤出血', '煎服,包煎', '2-6g', '风寒伏肺咳嗽失音者禁服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 177, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '马勃';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白头翁', '野丈人、胡王使者', '清热药', '寒', '苦', '归胃、大肠经', '清热解毒,凉血止痢', '热毒血痢,阴痒带下', '煎服', '9-15g', '虚寒泻痢者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 184, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白头翁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('马齿苋', '马齿菜、五行草', '清热药', '寒', '酸', '归肝、大肠经', '清热解毒,凉血止血,止痢', '热毒血痢,痈肿疔疮,湿疹,丹毒,蛇虫咬伤,便血,痔血,崩漏下血', '煎服', '9-15g', '脾胃虚寒者慎用,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 191, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '马齿苋';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鸦胆子', '老鸦胆、苦榛子', '清热药', '寒', '苦', '归大肠、肝经', '清热解毒,截疟,止痢,腐蚀赘疣', '痢疾,疟疾,赘疣,鸡眼', '内服去壳取仁,以龙眼肉包裹或装胶囊', '0.5-2g', '胃肠出血及肝肾病患者忌用,孕妇慎用', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 198, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鸦胆子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('败酱草', '败酱、鹿肠', '清热药', '微寒', '辛、苦', '归胃、大肠、肝经', '清热解毒,消痈排脓,祛瘀止痛', '肠痈,肺痈,痈肿疮毒,产后瘀阻腹痛', '煎服', '6-15g', '脾胃虚弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 35, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '败酱草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白花蛇舌草', '蛇舌草、羊须草', '清热药', '寒', '苦、甘', '归胃、大肠、小肠经', '清热解毒,利湿通淋', '痈肿疮毒,咽喉肿痛,毒蛇咬伤,热淋涩痛', '煎服', '15-30g', '阴疽及脾胃虚寒者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 42, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白花蛇舌草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('土茯苓', '禹余粮、白余粮', '清热药', '平', '甘、淡', '归肝、胃经', '解毒,除湿,通利关节', '梅毒及汞中毒所致的肢体拘挛,筋骨疼痛,湿热淋浊,带下,痈肿,瘰疬,疥癣', '煎服', '15-60g', '肝肾阴虚者慎服,服药时忌茶', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 49, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '土茯苓';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('熊胆粉', '熊胆', '清热药', '寒', '苦', '归肝、胆、心经', '清热解毒,息风止痉,清肝明目', '热病惊痫,小儿惊风,癫痫,抽搐,黄疸,胆石症,目赤肿痛,翳膜遮睛,痈肿疮毒,咽喉肿痛', '内服多入丸散', '0.25-0.5g', '虚寒证禁用,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 56, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '熊胆粉';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('生地黄', '干地黄、生地', '清热药', '寒', '甘、苦', '归心、肝、肾经', '清热凉血,养阴生津', '热入营血,舌绛烦渴,斑疹吐衄,热病伤阴,阴虚发热,骨蒸劳热,内热消渴', '煎服', '10-15g', '脾虚湿滞,腹满便溏者不宜使用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 63, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '生地黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('玄参', '元参、黑参', '清热药', '微寒', '苦、甘、咸', '归肺、胃、肾经', '清热凉血,滋阴降火,解毒散结', '热入营血,舌绛烦渴,温毒发斑,津伤便秘,骨蒸劳嗽,目赤,咽痛,白喉,痈肿疮毒,瘰疬', '煎服', '9-15g', '脾胃虚寒,食少便溏者不宜使用,不宜与藜芦同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 70, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '玄参';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('牡丹皮', '丹皮、粉丹皮', '清热药', '微寒', '苦、辛', '归心、肝、肾经', '清热凉血,活血化瘀', '热入营血,温毒发斑,吐血衄血,夜热早凉,无汗骨蒸,经闭痛经,跌扑伤痛,痈肿疮毒', '煎服', '6-12g', '血虚有寒,月经过多及孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 77, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '牡丹皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('赤芍', '赤芍药、红芍药', '清热药', '微寒', '苦', '归肝经', '清热凉血,散瘀止痛', '热入营血,温毒发斑,吐血衄血,目赤肿痛,肝郁胁痛,经闭痛经,癥瘕腹痛,跌扑损伤,痈肿疮疡', '煎服', '6-12g', '血虚经闭者不宜用,不宜与藜芦同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 84, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '赤芍';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫草', '紫丹、地血', '清热药', '寒', '甘、咸', '归心、肝经', '清热凉血,活血解毒,透疹消斑', '血热毒盛,斑疹紫黑,麻疹不透,疮疡,湿疹,水火烫伤', '煎服', '5-9g', '脾胃虚寒便溏者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 91, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '紫草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('水牛角', '牛角', '清热药', '寒', '苦', '归心、肝经', '清热凉血,解毒,定惊', '温病高热,神昏谵语,惊风,癫狂,血热妄行斑疹,吐衄,痈肿疮疡,咽喉肿痛', '镑片或粗粉煎服,宜先煎3小时以上', '15-30g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 98, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '水牛角';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('青蒿', '蒿、草蒿', '清热药', '寒', '苦、辛', '归肝、胆经', '清虚热,除骨蒸,解暑热,截疟,退黄', '温邪伤阴,夜热早凉,阴虚发热,骨蒸劳热,暑邪发热,疟疾寒热,湿热黄疸', '煎服,后下', '6-12g', '脾胃虚弱,肠滑泄泻者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 105, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '青蒿';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白薇', '薇草、白微', '清热药', '寒', '苦、咸', '归胃、肝、肾经', '清热凉血,利尿通淋,解毒疗疮', '温邪伤营发热,阴虚发热,骨蒸劳热,产后血虚发热,热淋,血淋,痈疽肿毒', '煎服', '5-10g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 112, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白薇';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('地骨皮', '枸杞根皮、地骨', '清热药', '寒', '甘', '归肺、肝、肾经', '凉血除蒸,清肺降火', '阴虚潮热,骨蒸盗汗,肺热咳嗽,咯血,衄血,内热消渴', '煎服', '9-15g', '外感风寒发热及脾虚便溏者不宜用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 119, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '地骨皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('银柴胡', '银胡、山菜根', '清热药', '微寒', '甘', '归肝、胃经', '清虚热,除疳热', '阴虚发热,骨蒸劳热,小儿疳热', '煎服', '3-9g', '外感风寒,血虚无热者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 126, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '银柴胡';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('胡黄连', '胡连、割孤露泽', '清热药', '寒', '苦', '归肝、胃、大肠经', '退虚热,除疳热,清湿热', '骨蒸潮热,小儿疳热,湿热泻痢,黄疸尿赤,痔疮肿痛', '煎服', '3-9g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 133, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '胡黄连';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('巴豆', '巴菽、刚子', '泻下药', '热', '辛', '归胃、大肠经', '峻下冷积,逐水退肿,祛痰利咽,外用蚀疮', '寒积便秘,乳食停滞,腹水鼓胀,二便不通,喉风,喉痹,痈肿脓成未溃,疥癣恶疮', '入丸散服', '0.1-0.3g', '孕妇及体弱者忌用,不宜与牵牛子同用', '有大毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 140, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '巴豆';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('川乌', '川乌头、乌喙', '祛风湿药', '热', '苦、辛', '归心、肝、肾、脾经', '祛风除湿,温经止痛', '风寒湿痹,关节疼痛,心腹冷痛,寒疝作痛,跌扑伤痛', '煎服,先煎、久煎', '1.5-3g', '孕妇忌用,不宜与半夏、瓜蒌、贝母、白蔹、白及同用', '有毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 147, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '川乌';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('草乌', '草乌头、乌头', '祛风湿药', '热', '苦、辛', '归心、肝、肾、脾经', '祛风除湿,温经止痛', '风寒湿痹,关节疼痛,心腹冷痛,寒疝作痛,跌扑伤痛', '煎服,先煎、久煎', '1.5-3g', '孕妇忌用,不宜与半夏、瓜蒌、贝母、白蔹、白及同用', '有毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 154, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '草乌';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蚕沙', '蚕矢、晚蚕沙', '祛风湿药', '温', '甘、辛', '归肝、脾、胃经', '祛风除湿,和胃化湿', '风湿痹痛,肢体不遂,湿疹瘙痒,吐泻转筋', '煎服,包煎', '5-15g', '血虚手足不遂者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 161, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蚕沙';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('伸筋草', '石松、过山龙', '祛风湿药', '温', '微苦、辛', '归肝、脾、肾经', '祛风除湿,舒筋活络', '关节酸痛,屈伸不利', '煎服', '3-12g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 168, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '伸筋草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('寻骨风', '清骨风、白毛藤', '祛风湿药', '平', '苦', '归肝经', '祛风除湿,通络止痛', '风湿痹痛,肢体麻木,筋脉拘挛,跌打损伤', '煎服', '9-15g', '阴虚内热者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 175, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '寻骨风';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('松节', '油松节、松郎头', '祛风湿药', '温', '苦', '归肝、肾经', '祛风除湿,通络止痛', '风寒湿痹,历节风痛,转筋挛急,跌打损伤', '煎服', '9-15g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 182, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '松节';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('海风藤', '风藤、巴岩香', '祛风湿药', '微温', '辛、苦', '归肝经', '祛风湿,通经络,止痹痛', '风寒湿痹,肢节疼痛,筋脉拘挛,屈伸不利', '煎服', '6-12g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 189, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '海风藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('青风藤', '清风藤、青藤', '祛风湿药', '平', '苦、辛', '归肝、脾经', '祛风湿,通经络,利小便', '风湿痹痛,关节肿胀,麻痹瘙痒', '煎服', '6-12g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 196, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '青风藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('丁公藤', '麻辣子、包公藤', '祛风湿药', '温', '辛', '归肝、脾、胃经', '祛风除湿,消肿止痛', '风湿痹痛,半身不遂,跌扑肿痛', '煎服,或酒浸服', '3-6g', '孕妇忌服,体质虚弱者慎用', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 33, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '丁公藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('络石藤', '络石、石鲮', '祛风湿药', '微寒', '苦', '归心、肝、肾经', '祛风通络,凉血消肿', '风湿热痹,筋脉拘挛,腰膝酸痛,喉痹,痈肿,跌扑损伤', '煎服', '6-12g', '阳虚畏寒,便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 40, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '络石藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桑枝', '桑条、嫩桑枝', '祛风湿药', '平', '微苦', '归肝经', '祛风湿,利关节', '风湿痹病,肩臂、关节酸痛麻木', '煎服', '9-15g', '寒饮停聚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 47, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桑枝';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('老鹳草', '老鹳嘴、老鸦嘴', '祛风湿药', '平', '辛、苦', '归肝、肾、脾经', '祛风湿,通经络,止泻痢', '风湿痹痛,麻木拘挛,筋骨酸痛,泄泻痢疾', '煎服', '9-15g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 54, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '老鹳草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('穿山龙', '穿龙骨、地龙骨', '祛风湿药', '温', '甘、苦', '归肝、肾、肺经', '祛风除湿,舒筋通络,活血止痛,止咳平喘', '风湿痹病,关节肿胀,疼痛麻木,跌扑损伤,闪腰岔气,咳嗽气喘', '煎服', '9-15g', '粉碎时注意防护,以免引起过敏', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 61, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '穿山龙';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('丝瓜络', '丝瓜网、丝瓜壳', '祛风湿药', '平', '甘', '归肺、胃、肝经', '祛风,通络,活血,下乳', '痹痛拘挛,胸胁胀痛,乳汁不通,乳痈肿痛', '煎服', '5-12g', '寒饮停聚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 68, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '丝瓜络';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('狗脊', '金毛狗脊、金狗脊', '祛风湿药', '温', '苦、甘', '归肝、肾经', '祛风湿,补肝肾,强腰膝', '风湿痹痛,腰膝酸软,下肢无力,尿频,遗尿,白带过多', '煎服', '6-12g', '肾虚有热,小便不利者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 75, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '狗脊';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('千年健', '一包针、千颗针', '祛风湿药', '温', '苦、辛', '归肝、肾经', '祛风湿,壮筋骨', '风寒湿痹,腰膝冷痛,下肢拘挛麻木', '煎服,或酒浸服', '5-10g', '阴虚内热者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 82, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '千年健';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('雪莲花', '雪莲、大木花', '祛风湿药', '温', '甘、微苦', '归肝、肾经', '温肾壮阳,调经止血', '阳痿,腰膝酸软,妇女崩漏,月经不调,风湿痹痛,外伤出血', '煎服', '6-12g', '孕妇忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 89, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '雪莲花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鹿衔草', '鹿蹄草、鹿含草', '祛风湿药', '温', '甘、苦', '归肝、肾经', '祛风湿,强筋骨,止血', '风湿痹痛,腰膝无力,月经过多,久咳劳嗽', '煎服', '9-15g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 96, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鹿衔草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('豆蔻', '白豆蔻、圆豆蔻', '化湿药', '温', '辛', '归肺、脾、胃经', '化湿行气,温中止呕,开胃消食', '湿浊中阻,不思饮食,湿温初起,胸闷不饥,寒湿呕逆,胸腹胀痛,食积不消', '煎服,后下', '3-6g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 103, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '豆蔻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('天南星', '南星、虎掌', '化痰止咳平喘药', '温', '苦、辛', '归肺、肝、脾经', '燥湿化痰,祛风止痉,散结消肿', '顽痰咳嗽,风痰眩晕,中风痰壅,口眼歪斜,半身不遂,癫痫,惊风,破伤风,痈疽肿痛,瘰疬痰核,毒蛇咬伤', '煎服,内服宜制用', '3-9g', '阴虚燥痰者及孕妇忌用', '有毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 110, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '天南星';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白附子', '禹白附、独角莲', '化痰止咳平喘药', '温', '辛、甘', '归胃、肝经', '祛风痰,定惊搐,解毒散结,止痛', '中风痰壅,口眼歪斜,语言謇涩,惊风癫痫,破伤风,痰厥头痛,偏正头痛,瘰疬痰核,毒蛇咬伤', '煎服,内服宜制用', '3-6g', '孕妇慎用,生品内服宜慎', '有毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 117, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白附子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白芥子', '芥子、辣菜子', '化痰止咳平喘药', '温', '辛', '归肺、胃经', '温肺豁痰利气,散结通络止痛', '寒痰喘咳,胸胁胀痛,痰滞经络,关节麻木,疼痛,痰湿流注,阴疽肿毒', '煎服', '3-9g', '肺虚咳嗽,阴虚火旺者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 124, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白芥子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('皂荚', '皂角、大皂荚', '化痰止咳平喘药', '温', '辛、咸', '归肺、大肠经', '祛顽痰,通窍开闭,祛风杀虫', '顽痰阻肺,咳喘痰多,卒然昏迷,中风牙关紧闭,癫痫痰盛,窍闭神昏,喉痹痰阻,顽痰便秘', '煎服,多入丸散', '1-1.5g', '孕妇忌服,咯血者禁用', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 131, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '皂荚';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('旋覆花', '金沸草、六月菊', '化痰止咳平喘药', '微温', '苦、辛、咸', '归肺、脾、胃、大肠经', '降气,消痰,行水,止呕', '风寒咳嗽,痰饮蓄结,胸膈痞闷,喘咳痰多,呕吐噫气,心下痞硬', '煎服,包煎', '3-9g', '阴虚劳嗽,肺燥咳嗽者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 138, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '旋覆花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白前', '鹅管白前、竹叶白前', '化痰止咳平喘药', '微温', '辛、苦', '归肺经', '降气,消痰,止咳', '肺气壅实,咳嗽痰多,胸满喘急', '煎服', '3-9g', '肺虚干咳者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 145, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白前';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('前胡', '白花前胡、紫花前胡', '化痰止咳平喘药', '微寒', '苦、辛', '归肺经', '降气化痰,散风清热', '痰热喘满,咯痰黄稠,风热咳嗽,痰多气急', '煎服', '3-9g', '阴虚咳嗽,寒饮咳嗽者禁服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 152, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '前胡';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桔梗', '苦桔梗、白桔梗', '化痰止咳平喘药', '平', '苦、辛', '归肺经', '宣肺,利咽,祛痰,排脓', '咳嗽痰多,胸闷不畅,咽痛音哑,肺痈吐脓,疮疡脓成不溃', '煎服', '3-9g', '阴虚久咳,咯血者禁服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 159, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桔梗';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('川贝母', '川贝、青贝', '化痰止咳平喘药', '微寒', '苦、甘', '归肺、心经', '清热润肺,化痰止咳,散结消痈', '肺热燥咳,干咳少痰,阴虚劳嗽,痰中带血,瘰疬,乳痈,肺痈', '煎服,研粉冲服', '3-9g,研粉1-2g', '不宜与川乌、草乌同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 166, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '川贝母';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('浙贝母', '浙贝、大贝', '化痰止咳平喘药', '寒', '苦', '归肺、心经', '清热化痰止咳,解毒散结消痈', '风热咳嗽,痰火咳嗽,肺痈,乳痈,瘰疬,疮毒', '煎服', '5-10g', '不宜与川乌、草乌同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 173, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '浙贝母';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('瓜蒌', '栝楼、糖瓜蒌', '化痰止咳平喘药', '寒', '甘、微苦', '归肺、胃、大肠经', '清热涤痰,宽胸散结,润燥滑肠', '肺热咳嗽,痰浊黄稠,胸痹心痛,结胸痞满,乳痈,肺痈,肠痈,大便秘结', '煎服', '9-15g', '脾胃虚寒,大便不实者忌用,不宜与川乌、草乌同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 180, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '瓜蒌';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('竹茹', '竹皮、青竹茹', '化痰止咳平喘药', '微寒', '甘', '归肺、胃、心、胆经', '清热化痰,除烦,止呕', '痰热咳嗽,胆火挟痰,烦热呕吐,惊悸失眠,中风痰迷,舌强不语,胃热呕吐,妊娠恶阻,胎动不安', '煎服', '5-10g', '胃寒呕吐者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 187, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '竹茹';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('竹沥', '竹汁、淡竹沥', '化痰止咳平喘药', '寒', '甘', '归心、肺、肝经', '清热豁痰,定惊利窍', '痰热咳嗽,中风痰迷,惊痫癫狂,痰稠难咯', '冲服', '15-30ml', '寒痰,便溏者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 194, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '竹沥';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('天竺黄', '天竹黄、竹黄', '化痰止咳平喘药', '寒', '甘', '归心、肝经', '清热豁痰,凉心定惊', '热病神昏,中风痰迷,小儿痰热惊痫,抽搐,夜啼', '煎服', '3-9g', '寒痰者禁用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 31, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '天竺黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('海藻', '海萝、海带花', '化痰止咳平喘药', '寒', '苦、咸', '归肝、胃、肾经', '消痰软坚散结,利水消肿', '瘿瘤,瘰疬,睾丸肿痛,痰饮水肿', '煎服', '6-12g', '不宜与甘草同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 38, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '海藻';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('昆布', '海带、纶布', '化痰止咳平喘药', '寒', '咸', '归肝、胃、肾经', '消痰软坚散结,利水消肿', '瘿瘤,瘰疬,睾丸肿痛,痰饮水肿', '煎服', '6-12g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 45, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '昆布';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('蛤壳', '海蛤壳、文蛤', '化痰止咳平喘药', '寒', '苦、咸', '归肺、肾、胃经', '清热化痰,软坚散结,制酸止痛,利尿消肿', '痰火咳嗽,胸胁疼痛,痰中带血,瘰疬,瘿瘤,痰核,胃痛泛酸,水肿,小便不利', '煎服,先煎,蛤粉宜包煎', '6-15g', '脾胃虚寒者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 52, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '蛤壳';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('浮海石', '海浮石、浮石', '化痰止咳平喘药', '寒', '咸', '归肺、肾经', '清肺化痰,软坚散结,利尿通淋', '痰热咳嗽,瘿瘤,瘰疬,血淋,石淋', '煎服,打碎先煎', '9-15g', '虚寒咳嗽者禁服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 59, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '浮海石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('礞石', '青礞石、金礞石', '化痰止咳平喘药', '平', '甘、咸', '归肺、心、肝经', '坠痰下气,平肝镇惊', '顽痰胶结,咳逆喘急,癫痫发狂,烦躁胸闷,惊风抽搐', '煎服,多入丸散', '3-6g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 66, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '礞石';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('苦杏仁', '杏仁、北杏仁', '化痰止咳平喘药', '微温', '苦', '归肺、大肠经', '降气止咳平喘,润肠通便', '咳嗽气喘,胸满痰多,血虚津枯,肠燥便秘', '煎服,宜后下', '5-10g', '阴虚咳嗽,大便溏泄者慎用,有小毒', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 73, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '苦杏仁';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫苏子', '苏子、黑苏子', '化痰止咳平喘药', '温', '辛', '归肺、大肠经', '降气化痰,止咳平喘,润肠通便', '痰壅气逆,咳嗽气喘,肠燥便秘', '煎服', '3-9g', '脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 80, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '紫苏子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('百部', '百条根、闹虱药', '化痰止咳平喘药', '微温', '甘、苦', '归肺经', '润肺下气止咳,杀虫灭虱', '新久咳嗽,肺痨咳嗽,百日咳,头虱,体虱,蛲虫病,阴痒', '煎服', '3-9g', '脾胃虚弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 87, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '百部';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('紫菀', '紫苑、青菀', '化痰止咳平喘药', '温', '苦、辛、甘', '归肺经', '润肺下气,化痰止咳', '痰多喘咳,新久咳嗽,劳嗽咳血', '煎服', '5-9g', '阴虚燥咳者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 94, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '紫菀';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('款冬花', '冬花、款花', '化痰止咳平喘药', '温', '辛、微苦', '归肺经', '润肺下气,止咳化痰', '新久咳嗽,喘咳痰多,劳嗽咳血', '煎服', '5-9g', '肺火燔灼者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 101, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '款冬花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('马兜铃', '兜铃、马兜零', '化痰止咳平喘药', '寒', '苦、微辛', '归肺、大肠经', '清肺降气,止咳平喘,清肠消痔', '肺热咳喘,痰中带血,肠热痔血,痔疮肿痛', '煎服', '3-9g', '虚寒咳喘,脾虚便溏者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 108, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '马兜铃';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('枇杷叶', '巴叶、芦桔叶', '化痰止咳平喘药', '微寒', '苦', '归肺、胃经', '清肺止咳,降逆止呕', '肺热咳嗽,气逆喘急,胃热呕逆,烦热口渴', '煎服,刷去毛,包煎', '6-9g', '胃寒呕吐,肺感风寒咳嗽者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 115, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '枇杷叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('桑白皮', '桑根白皮、桑皮', '化痰止咳平喘药', '寒', '甘', '归肺经', '泻肺平喘,利水消肿', '肺热喘咳,水肿胀满,尿少,面目肌肤浮肿', '煎服', '6-12g', '肺寒咳嗽者忌用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 122, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '桑白皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('葶苈子', '大适、丁历', '化痰止咳平喘药', '大寒', '苦、辛', '归肺、膀胱经', '泻肺平喘,行水消肿', '痰涎壅肺,喘咳痰多,胸胁胀满,不得平卧,胸腹水肿,小便不利,肺原性心脏病水肿', '煎服,包煎', '3-9g', '肺虚喘咳,脾虚肿满者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 129, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '葶苈子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白果', '银杏、鸭脚子', '化痰止咳平喘药', '平', '甘、苦、涩', '归肺、肾经', '敛肺定喘,止带缩尿', '痰多喘咳,带下白浊,遗尿尿频', '煎服', '5-10g', '有实邪者忌服,生食有毒', '有毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 136, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白果';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('洋金花', '曼陀罗花、风茄花', '化痰止咳平喘药', '温', '辛', '归肺、肝经', '平喘止咳,解痉定痛,安神', '哮喘咳嗽,脘腹冷痛,风湿痹痛,癫痫,惊风,外科麻醉', '内服多入丸散', '0.3-0.6g', '孕妇,外感,痰热咳喘,青光眼,高血压,心动过速者禁用', '有毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 143, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '洋金花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('青皮', '青橘皮、小青皮', '理气药', '温', '苦、辛', '归肝、胆、胃经', '疏肝破气,消积化滞', '胸胁胀痛,疝气疼痛,乳癖,乳痈,食积气滞,脘腹胀痛', '煎服', '3-9g', '气虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 150, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '青皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('枳壳', '江枳壳、川枳壳', '理气药', '微寒', '苦、辛、酸', '归脾、胃、大肠经', '理气宽中,行滞消胀', '胸胁气滞,胀满疼痛,食积不化,痰饮内停,脏器下垂', '煎服', '3-9g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 157, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '枳壳';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('木香', '广木香、云木香', '理气药', '温', '辛、苦', '归脾、胃、大肠、三焦、胆经', '行气止痛,健脾消食', '胸胁胀痛,脘腹胀痛,呕吐泄泻,痢疾后重,食积不消,不思饮食', '煎服,后下', '3-6g', '阴虚津液不足者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 164, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '木香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('香附', '香附子、莎草根', '理气药', '平', '辛、微苦、微甘', '归肝、脾、三焦经', '疏肝解郁,理气宽中,调经止痛', '肝郁气滞,胸胁胀痛,疝气疼痛,乳房胀痛,脾胃气滞,脘腹痞闷,月经不调,经闭痛经', '煎服', '6-9g', '气虚无滞者慎用,阴虚血热者忌服', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 171, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '香附';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('乌药', '天台乌药、矮樟', '理气药', '温', '辛', '归肺、脾、肾、膀胱经', '行气止痛,温肾散寒', '寒凝气滞,胸腹胀痛,气逆喘急,膀胱虚冷,遗尿尿频,疝气疼痛,痛经', '煎服', '6-9g', '气虚,有内热者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 178, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '乌药';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('沉香', '沉水香、蜜香', '理气药', '微温', '辛、苦', '归脾、胃、肾经', '行气止痛,温中止呕,纳气平喘', '胸腹胀闷疼痛,胃寒呕吐呃逆,肾虚气逆喘急', '煎服,后下,或研末冲服', '1-5g,研末0.5-1g', '阴虚火旺,气虚下陷者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 185, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '沉香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('檀香', '白檀香、黄檀香', '理气药', '温', '辛', '归脾、胃、心、肺经', '行气温中,开窍止痛', '寒凝气滞,胸膈不舒,胸痹心痛,脘腹疼痛,呕吐食少', '煎服,后下', '2-5g', '阴虚火旺者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 192, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '檀香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('川楝子', '金铃子、苦楝子', '理气药', '寒', '苦', '归肝、小肠、膀胱经', '疏肝泄热,行气止痛,杀虫', '肝郁化火,胸胁脘腹胀痛,疝气疼痛,虫积腹痛', '煎服', '5-9g', '脾胃虚寒者慎用,有小毒', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 199, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '川楝子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('荔枝核', '荔仁、大荔核', '理气药', '温', '甘、微苦', '归肝、肾经', '行气散结,祛寒止痛', '寒疝腹痛,睾丸肿痛,肝胃不和,胃脘疼痛,妇女气滞血瘀,少腹疼痛', '煎服', '5-10g', '无寒湿气滞者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 36, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '荔枝核';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('薤白', '野薤、野蒜', '理气药', '温', '辛、苦', '归心、肺、胃、大肠经', '通阳散结,行气导滞', '胸痹心痛,脘腹痞满胀痛,泻痢后重', '煎服', '5-9g', '气虚者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 43, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '薤白';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('佛手', '佛手柑、五指柑', '理气药', '温', '辛、苦、酸', '归肝、脾、胃、肺经', '疏肝理气,和胃止痛,燥湿化痰', '肝胃气滞,胸胁胀痛,胃脘痞满,食少呕吐,咳嗽痰多', '煎服', '3-9g', '阴虚有火,无气滞者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 50, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '佛手';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('香橼', '枸橼、香圆', '理气药', '温', '辛、苦、酸', '归肝、脾、肺经', '疏肝理气,宽中,化痰', '肝胃气滞,胸胁胀痛,脘腹痞满,呕吐噫气,痰多咳嗽', '煎服', '3-9g', '阴虚血燥者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 57, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '香橼';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('玫瑰花', '徘徊花、刺玫花', '理气药', '温', '甘、微苦', '归肝、脾经', '行气解郁,和血,止痛', '肝胃气痛,食少呕恶,月经不调,跌扑伤痛', '煎服', '3-6g', '阴虚有火者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 64, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '玫瑰花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('梅花', '绿萼梅、白梅花', '理气药', '平', '微酸、苦', '归肝、胃、肺经', '疏肝和中,化痰散结', '肝胃气痛,郁闷心烦,梅核气,瘰疬疮毒', '煎服', '3-5g', '阴虚重症者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 71, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '梅花';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('谷芽', '稻芽、粟芽', '消食药', '温', '甘', '归脾、胃经', '消食和中,健脾开胃', '食积不消,腹胀口臭,脾胃虚弱,不饥食少', '煎服', '9-15g', '胃下垂者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 78, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '谷芽';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('莱菔子', '萝卜子、萝白子', '消食药', '平', '辛、甘', '归肺、脾、胃经', '消食除胀,降气化痰', '饮食停滞,脘腹胀痛,大便秘结,积滞泻痢,痰壅喘咳', '煎服', '5-12g', '气虚及无食积、痰滞者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 85, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '莱菔子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鸡内金', '鸡肫皮、鸡黄皮', '消食药', '平', '甘', '归脾、胃、小肠、膀胱经', '消食健胃,涩精止遗,通淋化石', '食积不消,呕吐泻痢,小儿疳积,遗尿,遗精,石淋涩痛,胆胀胁痛', '煎服,研末服', '3-9g,研末1.5-3g', '脾虚无积滞者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 92, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鸡内金';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('使君子', '留求子、五棱子', '驱虫药', '温', '甘', '归脾、胃经', '杀虫消积', '蛔虫病,蛲虫病,虫积腹痛,小儿疳积', '煎服,炒香嚼服', '9-12g,嚼服6-9g', '大量服用可致呃逆,眩晕,呕吐', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 99, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '使君子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('苦楝皮', '楝皮、苦楝根皮', '驱虫药', '寒', '苦', '归肝、脾、胃经', '杀虫,疗癣', '蛔虫病,蛲虫病,虫积腹痛,疥癣瘙痒', '煎服', '3-6g', '体弱者慎用,孕妇忌用', '有毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 106, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '苦楝皮';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('槟榔', '大腹子、海南子', '驱虫药', '温', '苦、辛', '归胃、大肠经', '杀虫,消积,行气,利水,截疟', '绦虫病,蛔虫病,姜片虫病,虫积腹痛,积滞泻痢,里急后重,水肿脚气,疟疾', '煎服', '3-9g,驱绦虫30-60g', '脾虚便溏者慎用,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 113, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '槟榔';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('南瓜子', '南瓜仁、白瓜子', '驱虫药', '平', '甘', '归胃、大肠经', '杀虫', '绦虫病,血吸虫病', '研粉,冷开水调服', '60-120g', '无特殊禁忌', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 120, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '南瓜子';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('仙鹤草', '龙芽草、脱力草', '止血药', '平', '苦、涩', '归心、肝经', '收敛止血,截疟,止痢,解毒,补虚', '咯血,吐血,崩漏下血,疟疾,血痢,痈肿疮毒,阴痒带下,脱力劳伤', '煎服', '6-12g', '外感初起者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 127, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '仙鹤草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('白及', '白芨、甘根', '止血药', '微寒', '苦、甘、涩', '归肺、肝、胃经', '收敛止血,消肿生肌', '咯血,吐血,外伤出血,疮疡肿毒,皮肤皲裂,肺结核咯血,溃疡病出血', '煎服,研末服', '6-15g,研末3-6g', '不宜与川乌、草乌同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 134, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '白及';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('棕榈炭', '棕榈、棕皮', '止血药', '平', '苦、涩', '归肺、肝、大肠经', '收敛止血', '吐血,衄血,尿血,便血,崩漏', '煎服', '3-9g', '瘀滞出血者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 141, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '棕榈炭';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('血余炭', '乱发炭、人发炭', '止血药', '平', '苦', '归肝、胃经', '收敛止血,化瘀,利尿', '吐血,咯血,衄血,血淋,尿血,便血,崩漏,外伤出血,小便不利', '煎服,研末服', '5-9g,研末1.5-3g', '胃弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 148, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '血余炭';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('藕节', '光藕节、藕节疤', '止血药', '平', '甘、涩', '归肝、肺、胃经', '收敛止血,化瘀', '吐血,咯血,衄血,尿血,崩漏', '煎服', '9-15g', '无特殊禁忌', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 155, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '藕节';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('艾叶', '艾蒿、家艾', '止血药', '温', '辛、苦', '归肝、脾、肾经', '温经止血,散寒止痛,外用祛湿止痒', '吐血,衄血,崩漏,月经过多,胎漏下血,少腹冷痛,经寒不调,宫冷不孕,外治皮肤瘙痒', '煎服,外用熏洗', '3-9g', '阴虚血热者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 162, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '艾叶';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('灶心土', '伏龙肝、灶中黄土', '止血药', '温', '辛', '归脾、胃经', '温中止血,止呕,止泻', '脾气虚寒,摄血无力所致的吐血,便血,崩漏,胃寒呕吐,妊娠呕吐', '煎服,包煎', '15-30g', '阴虚失血者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 169, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '灶心土';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('延胡索', '元胡、玄胡索', '活血化瘀药', '温', '辛、苦', '归心、肝、脾经', '活血,行气,止痛', '胸胁,脘腹疼痛,胸痹心痛,经闭痛经,产后瘀阻,跌扑肿痛', '煎服,研粉吞服', '3-9g,研粉1.5-3g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 176, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '延胡索';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('郁金', '玉金、白丝郁金', '活血化瘀药', '寒', '辛、苦', '归肝、心、肺经', '活血止痛,行气解郁,清心凉血,利胆退黄', '胸胁刺痛,胸痹心痛,经闭痛经,乳房胀痛,热病神昏,癫痫发狂,血热吐衄,黄疸尿赤', '煎服', '3-9g', '不宜与丁香同用,孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 183, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '郁金';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('姜黄', '黄姜、宝鼎香', '活血化瘀药', '温', '辛、苦', '归脾、肝经', '破血行气,通经止痛', '胸胁刺痛,胸痹心痛,痛经经闭,癥瘕,风湿肩臂疼痛,跌扑肿痛', '煎服', '3-9g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 190, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '姜黄';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('乳香', '熏陆香、马尾香', '活血化瘀药', '温', '辛、苦', '归心、肝、脾经', '活血定痛,消肿生肌', '胸痹心痛,胃脘疼痛,痛经经闭,产后瘀阻,癥瘕腹痛,风湿痹痛,筋脉拘挛,跌打损伤,痈肿疮疡', '煎服,或入丸散', '3-5g', '孕妇及胃弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 197, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '乳香';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('没药', '末药、明没药', '活血化瘀药', '平', '辛、苦', '归心、肝、脾经', '散瘀定痛,消肿生肌', '胸痹心痛,胃脘疼痛,痛经经闭,产后瘀阻,癥瘕腹痛,风湿痹痛,筋脉拘挛,跌打损伤,痈肿疮疡', '煎服,或入丸散', '3-5g', '孕妇及胃弱者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 34, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '没药';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('五灵脂', '灵脂、寒号虫粪', '活血化瘀药', '温', '苦、咸、甘', '归肝经', '活血止痛,化瘀止血', '胸痹心痛,脘腹胁痛,痛经经闭,产后瘀阻,跌扑肿痛', '煎服,包煎', '3-9g', '孕妇慎用,不宜与人参同用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 41, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '五灵脂';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('益母草', '茺蔚、坤草', '活血化瘀药', '微寒', '苦、辛', '归心、肝、膀胱经', '活血调经,利尿消肿,清热解毒', '月经不调,痛经经闭,恶露不尽,水肿尿少,疮疡肿毒', '煎服', '9-30g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 48, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '益母草';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('牛膝', '怀牛膝、川牛膝', '活血化瘀药', '平', '苦、甘、酸', '归肝、肾经', '逐瘀通经,补肝肾,强筋骨,利尿通淋,引血下行', '经闭,痛经,腰膝酸痛,筋骨无力,淋证,水肿,头痛,眩晕,牙痛,口舌生疮,吐血,衄血', '煎服', '5-12g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 55, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '牛膝';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('鸡血藤', '血风藤、三叶鸡血藤', '活血化瘀药', '温', '苦、甘', '归肝、肾经', '活血补血,调经止痛,舒筋活络', '月经不调,痛经,闭经,血虚萎黄,麻木瘫痪,风湿痹痛', '煎服', '9-15g', '月经过多者慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 62, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '鸡血藤';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('王不留行', '王不留、麦蓝菜', '活血化瘀药', '平', '苦', '归肝、胃经', '活血通经,下乳消肿,利尿通淋', '经闭,痛经,乳汁不下,乳痈肿痛,淋证涩痛', '煎服', '5-9g', '孕妇慎用', '', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 69, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '王不留行';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('土鳖虫', '地鳖虫、土元', '活血化瘀药', '寒', '咸', '归肝经', '破血逐瘀,续筋接骨', '跌打损伤,筋伤骨折,血瘀经闭,产后瘀阻腹痛,癥瘕痞块', '煎服,研末服', '3-9g,研末1-1.5g', '孕妇禁用', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 76, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '土鳖虫';

INSERT OR IGNORE INTO medicines (name, alias, category, nature, taste, meridian, efficacy, indications, usage, dosage, contraindication, notes, created_at, updated_at)
VALUES ('水蛭', '蚂蟥、马蛭', '活血化瘀药', '平', '咸、苦', '归肝经', '破血通经,逐瘀消癥', '血瘀经闭,癥瘕痞块,中风偏瘫,跌扑损伤', '煎服,研末服', '1.5-3g,研末0.3-0.5g', '孕妇禁用,体弱血虚者慎用', '有小毒', '2026-07-17 00:00:00', '2026-07-17 00:00:00');

INSERT OR IGNORE INTO inventory (medicine_id, quantity, unit, price, min_stock, notes, created_at, updated_at)
SELECT id, 1000, 'g', 83, 100, '', '2026-07-17 00:00:00', '2026-07-17 00:00:00'
FROM medicines WHERE name = '水蛭';
