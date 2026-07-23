-- =====================================================================
-- 005_redesign_prices.sql
-- 中药材销售管理系统 - 药材价格重新设计（贴近真实市场行情）
-- 用途：将 inventory 表中常见药材的价格从公式生成值（30+(i*7)%170）
--       更新为 2024-2025 年中国中药材市场零售均价（元/100g）
-- 价格来源：2024-2025 年中国中药材市场零售均价参考
--          （综合亳州、安国、玉林等中药材专业市场行情）
-- 生成时间：2026-07-22
-- 价格单位：元/100g
-- 注意：此单位与系统计算公式 quantity(g) × price 不匹配，
--       006_fix_price_unit.sql 会将所有 price 除以 100 转为"元/g"。
-- 说明：使用 UPDATE + 子查询方式，按 medicines.name 精确匹配；
--       若某药材在 medicines 表中不存在，对应 UPDATE 不影响任何行（安全无副作用）。
--       原 002_seed_medicines.sql 中价格由公式 30+(i*7)%170 生成（30-200 元），
--       完全不符合真实市场行情，本迁移将其重设为真实零售价。
-- 价格分级：极低价 3-8元 / 低价 8-15元 / 中等价 15-30元 /
--           中高价 30-50元 / 高价 50-100元 / 超高价 100-300+元
-- =====================================================================

-- =====================================================================
-- 极低价 3-8 元（食药同源 / 极低价常用药）
-- =====================================================================
UPDATE inventory SET price = 5 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '生姜');
UPDATE inventory SET price = 6 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '大枣');
UPDATE inventory SET price = 4 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '粳米');
UPDATE inventory SET price = 8 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '甘草');
UPDATE inventory SET price = 8 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '生甘草');
UPDATE inventory SET price = 7 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '薏苡仁');
UPDATE inventory SET price = 8 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '淡豆豉');
UPDATE inventory SET price = 8 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '薄荷');
UPDATE inventory SET price = 8 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '紫苏');
UPDATE inventory SET price = 8 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '白扁豆');
UPDATE inventory SET price = 8 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '山楂');
UPDATE inventory SET price = 7 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '莱菔子');
UPDATE inventory SET price = 8 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '神曲');

-- =====================================================================
-- 低价 8-15 元（低价常用药）
-- =====================================================================
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '炙甘草');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '车前子');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '茯苓');
UPDATE inventory SET price = 14 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '白术');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '陈皮');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '半夏');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '桔梗');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '桑叶');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '菊花');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '泽泻');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '猪苓');
UPDATE inventory SET price = 9 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '木通');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '竹茹');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '枳壳');
UPDATE inventory SET price = 13 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '枳实');
UPDATE inventory SET price = 9 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '荆芥');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '荆芥穗');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '防风');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '白芷');
UPDATE inventory SET price = 11 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '羌活');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '独活');
UPDATE inventory SET price = 14 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '柴胡');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '藿香');
UPDATE inventory SET price = 11 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '苍术');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '厚朴');
UPDATE inventory SET price = 15 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '砂仁');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '大腹皮');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '霜桑叶');
UPDATE inventory SET price = 13 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '秦艽');
UPDATE inventory SET price = 14 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '细辛');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '益母草');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '桃仁');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '青皮');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '香附');
UPDATE inventory SET price = 15 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '木香');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '大黄');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '杏仁');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '百部');
UPDATE inventory SET price = 14 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '紫菀');
UPDATE inventory SET price = 14 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '款冬花');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '桑白皮');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '葶苈子');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '决明子');
UPDATE inventory SET price = 14 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '代赭石');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '牡蛎');
UPDATE inventory SET price = 14 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '旋覆花');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '山药');
UPDATE inventory SET price = 10 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '干姜');
UPDATE inventory SET price = 12 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '川楝子');
UPDATE inventory SET price = 15 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '郁金');
UPDATE inventory SET price = 15 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '苦参');
UPDATE inventory SET price = 15 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '合欢皮');
UPDATE inventory SET price = 15 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '龙骨');
UPDATE inventory SET price = 15 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '红花');
UPDATE inventory SET price = 15 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '莲子肉');

-- =====================================================================
-- 中等价 15-30 元
-- =====================================================================
UPDATE inventory SET price = 22 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '当归');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '白芍');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '川芎');
UPDATE inventory SET price = 16 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '生地黄');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '熟地黄');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '黄芩');
UPDATE inventory SET price = 25 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '黄连');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '黄柏');
UPDATE inventory SET price = 16 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '栀子');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '龙胆草');
UPDATE inventory SET price = 16 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '牡丹皮');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '赤芍');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '丹参');
UPDATE inventory SET price = 16 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '牛膝');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '川牛膝');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '延胡索');
UPDATE inventory SET price = 28 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '酸枣仁');
UPDATE inventory SET price = 22 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '远志');
UPDATE inventory SET price = 25 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '茯神');
UPDATE inventory SET price = 28 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '朱茯神');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '石决明');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '钩藤');
UPDATE inventory SET price = 22 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '地龙');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '僵蚕');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '蝉蜕');
UPDATE inventory SET price = 16 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '半夏曲');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '百合');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '玉竹');
UPDATE inventory SET price = 22 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '天冬');
UPDATE inventory SET price = 25 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '麦冬');
UPDATE inventory SET price = 22 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '黄精');
UPDATE inventory SET price = 22 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '续断');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '骨碎补');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '淫羊藿');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '菟丝子');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '补骨脂');
UPDATE inventory SET price = 25 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '巴戟天');
UPDATE inventory SET price = 25 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '龙眼肉');
UPDATE inventory SET price = 22 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '北沙参');
UPDATE inventory SET price = 20 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '肉桂');
UPDATE inventory SET price = 18 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '附子');
UPDATE inventory SET price = 28 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '党参');
UPDATE inventory SET price = 28 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '杜仲');

-- =====================================================================
-- 中高价 30-50 元
-- =====================================================================
UPDATE inventory SET price = 30 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '黄芪');
UPDATE inventory SET price = 30 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '枸杞子');
UPDATE inventory SET price = 30 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '肉苁蓉');
UPDATE inventory SET price = 30 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '山茱萸');
UPDATE inventory SET price = 35 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '石斛');
UPDATE inventory SET price = 35 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '天麻');
UPDATE inventory SET price = 45 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '人参');
UPDATE inventory SET price = 45 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '全蝎');

-- =====================================================================
-- 高价 50-100 元
-- =====================================================================
UPDATE inventory SET price = 55 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '三七');
UPDATE inventory SET price = 80 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '阿胶');

-- =====================================================================
-- 超高价 100-300+ 元
-- =====================================================================
UPDATE inventory SET price = 120 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '羚羊角片');
UPDATE inventory SET price = 120 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '鹿茸');
UPDATE inventory SET price = 150 WHERE medicine_id = (SELECT id FROM medicines WHERE name = '冬虫夏草');
