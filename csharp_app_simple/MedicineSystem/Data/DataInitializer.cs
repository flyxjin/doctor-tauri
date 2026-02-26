using System;
using System.Collections.Generic;
using MedicineSystem.Models;

namespace MedicineSystem.Data
{
    public static class DataInitializer
    {
        public static void InitializeDefaultData(DataStore db)
        {
            if (db.HasData()) return;

            var defaultMedicines = GetDefaultMedicines();

            foreach (var medData in defaultMedicines)
            {
                var medicine = new Medicine
                {
                    Name = medData["name"].ToString(),
                    Alias = medData["alias"]?.ToString() ?? "",
                    Category = medData["category"]?.ToString() ?? "",
                    Nature = medData["nature"]?.ToString() ?? "",
                    Taste = medData["taste"]?.ToString() ?? "",
                    Meridian = medData["meridian"]?.ToString() ?? "",
                    Efficacy = medData["efficacy"]?.ToString() ?? "",
                    Indications = medData["indications"]?.ToString() ?? "",
                    Usage = medData["usage"]?.ToString() ?? "",
                    Dosage = medData["dosage"]?.ToString() ?? "",
                    Contraindication = medData["contraindication"]?.ToString() ?? "",
                    Notes = medData["notes"]?.ToString() ?? ""
                };

                int medId = db.AddMedicine(medicine);

                var inventory = new Inventory
                {
                    MedicineId = medId,
                    MedicineName = medicine.Name,
                    Quantity = Convert.ToDecimal(medData["quantity"]),
                    Unit = medData["unit"]?.ToString() ?? "g",
                    Price = Convert.ToDecimal(medData["price"]),
                    MinStock = Convert.ToDecimal(medData["min_stock"]),
                    Notes = ""
                };

                db.AddInventory(inventory);
            }
        }

        private static List<Dictionary<string, object>> GetDefaultMedicines()
        {
            return new List<Dictionary<string, object>>
            {
                new Dictionary<string, object> { { "name", "人参" }, { "alias", "黄参、地精、神草" }, { "category", "补虚药" }, { "nature", "温" }, { "taste", "甘、微苦" }, { "meridian", "归脾、肺、心经" }, { "efficacy", "大补元气，复脉固脱，补脾益肺，生津，安神" }, { "indications", "体虚欲脱，肢冷脉微,脾虚食少,肺虚喘咳,津伤口渴,内热消渴,久病虚羸,惊悸失眠,阳痿宫冷" }, { "usage", "煎服" }, { "dosage", "3-9g" }, { "contraindication", "实证、热证而正气不虚者忌服" }, { "notes", "" }, { "quantity", 500m }, { "unit", "g" }, { "price", 85m }, { "min_stock", 50m } },
                new Dictionary<string, object> { { "name", "黄芪" }, { "alias", "黄耆" }, { "category", "补虚药" }, { "nature", "微温" }, { "taste", "甘" }, { "meridian", "归脾、肺经" }, { "efficacy", "补气升阳，固表止汗,利水消肿,生津养血,行滞通痹,托毒排脓,敛疮生肌" }, { "indications", "气虚乏力,食少便溏,中气下陷,久泻脱肛,便血崩漏,表虚自汗,气虚水肿,内热消渴,血虚萎黄,半身不遂,痹痛麻木,痈疽难溃,久溃不敛" }, { "usage", "煎服" }, { "dosage", "9-30g" }, { "contraindication", "表实邪盛,气滞湿阻,食积停滞,痈疽初起或溃后热毒尚盛等实证,以及阴虚阳亢者,均须禁服" }, { "notes", "" }, { "quantity", 600m }, { "unit", "g" }, { "price", 42m }, { "min_stock", 60m } },
                new Dictionary<string, object> { { "name", "当归" }, { "alias", "干归" }, { "category", "补虚药" }, { "nature", "温" }, { "taste", "甘、辛" }, { "meridian", "归肝、心、脾经" }, { "efficacy", "补血活血,调经止痛,润肠通便" }, { "indications", "血虚萎黄,眩晕心悸,月经不调,经闭痛经,虚寒腹痛,风湿痹痛,跌扑损伤,痈疽疮疡,肠燥便秘" }, { "usage", "煎服" }, { "dosage", "6-12g" }, { "contraindication", "湿阻中满及大便溏泄者慎服" }, { "notes", "" }, { "quantity", 450m }, { "unit", "g" }, { "price", 58m }, { "min_stock", 45m } },
                new Dictionary<string, object> { { "name", "白芍" }, { "alias", "白芍药" }, { "category", "补虚药" }, { "nature", "微寒" }, { "taste", "苦、酸" }, { "meridian", "归肝、脾经" }, { "efficacy", "养血调经,敛阴止汗,柔肝止痛" }, { "indications", "血虚萎黄,月经不调,崩漏,自汗,盗汗,头痛眩晕,胁痛腹痛,四肢挛急,面色苍白" }, { "usage", "煎服" }, { "dosage", "6-15g" }, { "contraindication", "阳衰虚寒之证不宜用" }, { "notes", "" }, { "quantity", 400m }, { "unit", "g" }, { "price", 65m }, { "min_stock", 40m } },
                new Dictionary<string, object> { { "name", "熟地黄" }, { "alias", "熟地" }, { "category", "补虚药" }, { "nature", "微温" }, { "taste", "甘" }, { "meridian", "归肝、肾经" }, { "efficacy", "补血滋阴,益精填髓" }, { "indications", "血虚萎黄,眩晕心悸,月经不调,崩漏,肾虚喘咳,须发早白,消渴,便秘,肾虚腰痛" }, { "usage", "煎服" }, { "dosage", "9-30g" }, { "contraindication", "脾虚湿滞,腹满便溏,痰多者不宜使用" }, { "notes", "" }, { "quantity", 350m }, { "unit", "g" }, { "price", 75m }, { "min_stock", 35m } },
                new Dictionary<string, object> { { "name", "党参" }, { "alias", "上党参、中灵参" }, { "category", "补虚药" }, { "nature", "平" }, { "taste", "甘" }, { "meridian", "归脾、肺经" }, { "efficacy", "补中益气,健脾益肺,养血生津" }, { "indications", "脾肺气虚,食少便溏,四肢乏力,气血两亏,久泻脱肛,血虚萎黄" }, { "usage", "煎服" }, { "dosage", "9-30g" }, { "contraindication", "不宜与藜芦同用" }, { "notes", "" }, { "quantity", 550m }, { "unit", "g" }, { "price", 38m }, { "min_stock", 55m } },
                new Dictionary<string, object> { { "name", "白术" }, { "alias", "于术、浙术" }, { "category", "补虚药" }, { "nature", "温" }, { "taste", "苦、甘" }, { "meridian", "归脾、胃经" }, { "efficacy", "健脾益气,燥湿利水,止汗,安胎" }, { "indications", "脾虚食少,腹胀泄泻,痰饮眩悸,水肿,自汗,胎动不安" }, { "usage", "煎服" }, { "dosage", "6-12g" }, { "contraindication", "阴虚内热,津枯液燥者慎用" }, { "notes", "" }, { "quantity", 500m }, { "unit", "g" }, { "price", 35m }, { "min_stock", 50m } },
                new Dictionary<string, object> { { "name", "茯苓" }, { "alias", "云苓、松苓" }, { "category", "利水渗湿药" }, { "nature", "平" }, { "taste", "甘、淡" }, { "meridian", "归心、脾、肾经" }, { "efficacy", "利水渗湿,健脾宁心" }, { "indications", "水肿尿少,痰饮眩悸,脾虚食少,便溏泄泻,心神不安,惊悸失眠" }, { "usage", "煎服" }, { "dosage", "10-15g" }, { "contraindication", "阴虚而无湿热者慎用" }, { "notes", "" }, { "quantity", 450m }, { "unit", "g" }, { "price", 32m }, { "min_stock", 45m } },
                new Dictionary<string, object> { { "name", "甘草" }, { "alias", "国老、甜草" }, { "category", "补虚药" }, { "nature", "平" }, { "taste", "甘" }, { "meridian", "归心、肺、脾、胃经" }, { "efficacy", "补脾益气,清热解毒,祛痰止咳,缓急止痛" }, { "indications", "脾胃虚弱,倦怠乏力,心悸气短,咳嗽痰多,脘腹四肢挛急疼痛,痈肿疮毒" }, { "usage", "煎服" }, { "dosage", "2-10g" }, { "contraindication", "不宜与京大戟、芫花、甘遂同用" }, { "notes", "" }, { "quantity", 600m }, { "unit", "g" }, { "price", 25m }, { "min_stock", 60m } },
                new Dictionary<string, object> { { "name", "金银花" }, { "alias", "忍冬花、银花、双花" }, { "category", "清热药" }, { "nature", "寒" }, { "taste", "甘" }, { "meridian", "归肺、心、胃经" }, { "efficacy", "清热解毒,疏散风热" }, { "indications", "痈肿疔疮,喉痹,丹毒,热毒血痢,风热感冒,温病发热" }, { "usage", "煎服" }, { "dosage", "6-15g" }, { "contraindication", "脾胃虚寒及气虚疮疡脓清者不宜使用" }, { "notes", "" }, { "quantity", 400m }, { "unit", "g" }, { "price", 45m }, { "min_stock", 40m } },
                new Dictionary<string, object> { { "name", "连翘" }, { "alias", "连壳、黄花条" }, { "category", "清热药" }, { "nature", "微寒" }, { "taste", "苦" }, { "meridian", "归肺、心、小肠经" }, { "efficacy", "清热解毒,消肿散结,疏散风热" }, { "indications", "痈疽,瘰疬,乳痈,丹毒,风热感冒,温病初起,热入营血,高热烦渴" }, { "usage", "煎服" }, { "dosage", "6-15g" }, { "contraindication", "脾胃虚寒及气虚脓清者不宜使用" }, { "notes", "" }, { "quantity", 350m }, { "unit", "g" }, { "price", 42m }, { "min_stock", 35m } },
                new Dictionary<string, object> { { "name", "板蓝根" }, { "alias", "大青根、蓝靛根" }, { "category", "清热药" }, { "nature", "寒" }, { "taste", "苦" }, { "meridian", "归心、胃经" }, { "efficacy", "清热解毒,凉血利咽" }, { "indications", "温毒发斑,舌绛紫暗,烂喉丹痄,大头瘟疫" }, { "usage", "煎服" }, { "dosage", "9-15g" }, { "contraindication", "脾胃虚寒者慎用" }, { "notes", "" }, { "quantity", 300m }, { "unit", "g" }, { "price", 28m }, { "min_stock", 30m } },
                new Dictionary<string, object> { { "name", "蒲公英" }, { "alias", "黄花地丁、婆婆丁" }, { "category", "清热药" }, { "nature", "寒" }, { "taste", "苦、甘" }, { "meridian", "归肝、胃经" }, { "efficacy", "清热解毒,消肿散结,利尿通淋" }, { "indications", "疔疮肿毒,乳痈,肺痈,肠痈,湿热黄疸,热淋涩痛" }, { "usage", "煎服" }, { "dosage", "10-30g" }, { "contraindication", "用量过大可致缓泻" }, { "notes", "" }, { "quantity", 350m }, { "unit", "g" }, { "price", 22m }, { "min_stock", 35m } },
                new Dictionary<string, object> { { "name", "黄芩" }, { "alias", "条芩、子芩" }, { "category", "清热药" }, { "nature", "寒" }, { "taste", "苦" }, { "meridian", "归肺、胆、脾、大肠经" }, { "efficacy", "清热燥湿,泻火解毒,止血安胎" }, { "indications", "湿温、暑湿,胸闷呕恶,湿热痞满,泻痢,黄疸,肺热咳嗽,高热烦渴,血热吐衄,胎动不安" }, { "usage", "煎服" }, { "dosage", "3-10g" }, { "contraindication", "脾胃虚寒者慎用" }, { "notes", "" }, { "quantity", 400m }, { "unit", "g" }, { "price", 38m }, { "min_stock", 40m } },
                new Dictionary<string, object> { { "name", "黄连" }, { "alias", "川连、味连" }, { "category", "清热药" }, { "nature", "寒" }, { "taste", "苦" }, { "meridian", "归心、脾、胃、肝、胆、大肠经" }, { "efficacy", "清热燥湿,泻火解毒" }, { "indications", "湿热痞满,呕吐吞酸,泻痢,黄疸,高热神昏,心火亢盛,心烦不寐,血热吐衄,目赤牙痛,消渴,痈肿疔疮" }, { "usage", "煎服" }, { "dosage", "2-5g" }, { "contraindication", "脾胃虚寒者慎用,阴虚津伤者慎用" }, { "notes", "" }, { "quantity", 300m }, { "unit", "g" }, { "price", 85m }, { "min_stock", 30m } },
                new Dictionary<string, object> { { "name", "黄柏" }, { "alias", "川柏、关黄柏" }, { "category", "清热药" }, { "nature", "寒" }, { "taste", "苦" }, { "meridian", "归肾、膀胱经" }, { "efficacy", "清热燥湿,泻火除蒸,解毒疗疮" }, { "indications", "湿热泻痢,黄疸,带下,热淋,脚气,痿软,盗汗,遗精,疮疡肿毒,湿疹瘙痒" }, { "usage", "煎服" }, { "dosage", "3-12g" }, { "contraindication", "脾胃虚寒者慎用" }, { "notes", "" }, { "quantity", 350m }, { "unit", "g" }, { "price", 45m }, { "min_stock", 35m } },
                new Dictionary<string, object> { { "name", "麻黄" }, { "alias", "龙沙、狗骨" }, { "category", "解表药" }, { "nature", "温" }, { "taste", "辛、微苦" }, { "meridian", "归肺、膀胱经" }, { "efficacy", "发汗解表,宣肺平喘,利水消肿" }, { "indications", "风寒感冒,胸闷喘咳,风水浮肿,支气管哮喘" }, { "usage", "煎服" }, { "dosage", "2-9g" }, { "contraindication", "体虚自汗、盗汗、虚喘及高血压患者慎用" }, { "notes", "" }, { "quantity", 300m }, { "unit", "g" }, { "price", 25m }, { "min_stock", 30m } },
                new Dictionary<string, object> { { "name", "桂枝" }, { "alias", "柳桂" }, { "category", "解表药" }, { "nature", "温" }, { "taste", "辛、甘" }, { "meridian", "归心、肺、膀胱经" }, { "efficacy", "发汗解肌,温通经脉,助阳化气,平冲降逆" }, { "indications", "风寒感冒,脘腹冷痛,血寒经闭,关节痹痛,痰饮,水肿,心悸" }, { "usage", "煎服" }, { "dosage", "3-10g" }, { "contraindication", "孕妇及月经过多者慎用" }, { "notes", "" }, { "quantity", 350m }, { "unit", "g" }, { "price", 22m }, { "min_stock", 35m } },
                new Dictionary<string, object> { { "name", "柴胡" }, { "alias", "地熏、茈胡" }, { "category", "解表药" }, { "nature", "微寒" }, { "taste", "苦、辛" }, { "meridian", "归肝、胆、肺经" }, { "efficacy", "疏散退热,疏肝解郁,升举阳气" }, { "indications", "感冒发热,寒热往来,胸胁胀痛,月经不调,子宫脱垂,脱肛" }, { "usage", "煎服" }, { "dosage", "3-10g" }, { "contraindication", "肝阳上亢,肝风内动,阴虚火旺及气机上逆者忌用或慎用" }, { "notes", "" }, { "quantity", 400m }, { "unit", "g" }, { "price", 35m }, { "min_stock", 40m } },
                new Dictionary<string, object> { { "name", "川芎" }, { "alias", "芎藭、小叶川芎" }, { "category", "活血化瘀药" }, { "nature", "温" }, { "taste", "辛" }, { "meridian", "归肝、胆、心包经" }, { "efficacy", "活血行气,祛风止痛" }, { "indications", "胸痹心痛,胸胁刺痛,跌扑肿痛,月经不调,经闭痛经,产后瘀滞腹痛,头痛,风湿痹痛" }, { "usage", "煎服" }, { "dosage", "3-10g" }, { "contraindication", "阴虚火旺,多汗,热盛及无瘀之出血证和孕妇慎用" }, { "notes", "" }, { "quantity", 380m }, { "unit", "g" }, { "price", 48m }, { "min_stock", 38m } },
                new Dictionary<string, object> { { "name", "丹参" }, { "alias", "红参、紫丹参" }, { "category", "活血化瘀药" }, { "nature", "微寒" }, { "taste", "苦" }, { "meridian", "归心、心包、肝经" }, { "efficacy", "活血祛瘀,通经止痛,清心除烦,凉血消痈" }, { "indications", "胸痹心痛,脘腹胁痛,癥瘕积聚,热痹疼痛,心烦不眠,月经不调,痛经经闭,疮疡肿痛" }, { "usage", "煎服" }, { "dosage", "10-15g" }, { "contraindication", "不宜与藜芦同用" }, { "notes", "" }, { "quantity", 380m }, { "unit", "g" }, { "price", 42m }, { "min_stock", 38m } },
                new Dictionary<string, object> { { "name", "红花" }, { "alias", "红蓝花、刺红花" }, { "category", "活血化瘀药" }, { "nature", "温" }, { "taste", "辛" }, { "meridian", "归心、肝经" }, { "efficacy", "活血通经,散瘀止痛" }, { "indications", "经闭,痛经,恶露不行,癥瘕痞块,胸痹心痛,瘀滞腹痛,胸胁刺痛,跌扑损伤,疮疡肿痛" }, { "usage", "煎服" }, { "dosage", "3-10g" }, { "contraindication", "孕妇慎用" }, { "notes", "" }, { "quantity", 300m }, { "unit", "g" }, { "price", 55m }, { "min_stock", 30m } },
                new Dictionary<string, object> { { "name", "桃仁" }, { "alias", "桃核仁" }, { "category", "活血化瘀药" }, { "nature", "平" }, { "taste", "苦、甘" }, { "meridian", "归心、肝、大肠经" }, { "efficacy", "活血祛瘀,润肠通便,止咳平喘" }, { "indications", "经闭痛经,癥瘕痞块,肺痈肠痈,跌扑损伤,肠燥便秘,咳嗽气喘" }, { "usage", "煎服" }, { "dosage", "5-10g" }, { "contraindication", "孕妇慎用" }, { "notes", "" }, { "quantity", 320m }, { "unit", "g" }, { "price", 35m }, { "min_stock", 32m } },
                new Dictionary<string, object> { { "name", "陈皮" }, { "alias", "橘皮" }, { "category", "理气药" }, { "nature", "温" }, { "taste", "苦、辛" }, { "meridian", "归脾、肺经" }, { "efficacy", "理气健脾,燥湿化痰" }, { "indications", "脘腹胀满,食少吐泻,咳嗽痰多" }, { "usage", "煎服" }, { "dosage", "3-10g" }, { "contraindication", "阴虚燥咳者慎用" }, { "notes", "" }, { "quantity", 600m }, { "unit", "g" }, { "price", 15m }, { "min_stock", 60m } },
                new Dictionary<string, object> { { "name", "半夏" }, { "alias", "地文、羊眼半夏" }, { "category", "化痰止咳平喘药" }, { "nature", "温" }, { "taste", "辛" }, { "meridian", "归脾、胃、肺经" }, { "efficacy", "燥湿化痰,降逆止呕,消痞散结" }, { "indications", "湿痰寒痰,咳喘痰多,痰饮眩悸,风痰眩晕,痰厥头痛,呕吐反胃,胸脘痞闷,梅核气" }, { "usage", "煎服" }, { "dosage", "3-9g" }, { "contraindication", "不宜与川乌、制川乌、草乌、制草乌、附子同用" }, { "notes", "生品有毒" }, { "quantity", 400m }, { "unit", "g" }, { "price", 22m }, { "min_stock", 40m } },
                new Dictionary<string, object> { { "name", "枸杞子" }, { "alias", "苟起子、枸杞红实" }, { "category", "补虚药" }, { "nature", "平" }, { "taste", "甘" }, { "meridian", "归肝、肾经" }, { "efficacy", "滋补肝肾,益精明目" }, { "indications", "虚劳精亏,腰膝酸痛,眩晕耳鸣,阳痿遗精,内热消渴,血虚萎黄,目昏不明" }, { "usage", "煎服" }, { "dosage", "6-12g" }, { "contraindication", "外邪实热者慎用" }, { "notes", "" }, { "quantity", 300m }, { "unit", "g" }, { "price", 65m }, { "min_stock", 30m } },
                new Dictionary<string, object> { { "name", "山药" }, { "alias", "怀山药、淮山" }, { "category", "补虚药" }, { "nature", "平" }, { "taste", "甘" }, { "meridian", "归脾、肺、肾经" }, { "efficacy", "补脾养胃,生津益肺,补肾涩精" }, { "indications", "脾虚食少,久泻不止,肺虚喘咳,肾虚遗精,带下,尿频,虚热消渴" }, { "usage", "煎服" }, { "dosage", "15-30g" }, { "contraindication", "湿盛中满者慎用" }, { "notes", "" }, { "quantity", 450m }, { "unit", "g" }, { "price", 25m }, { "min_stock", 45m } },
                new Dictionary<string, object> { { "name", "山茱萸" }, { "alias", "山萸肉、肉枣" }, { "category", "收涩药" }, { "nature", "微温" }, { "taste", "酸、涩" }, { "meridian", "归肝、肾经" }, { "efficacy", "补益肝肾,收涩固脱" }, { "indications", "眩晕耳鸣,腰膝酸痛,阳痿遗精,遗尿尿频,崩漏带下,大汗虚脱,内热消渴" }, { "usage", "煎服" }, { "dosage", "6-12g" }, { "contraindication", "湿热体质者慎用" }, { "notes", "" }, { "quantity", 280m }, { "unit", "g" }, { "price", 58m }, { "min_stock", 28m } },
                new Dictionary<string, object> { { "name", "杜仲" }, { "alias", "思仙、木绵" }, { "category", "补虚药" }, { "nature", "温" }, { "taste", "甘" }, { "meridian", "归肝、肾经" }, { "efficacy", "补肝肾,强筋骨,安胎" }, { "indications", "肾虚腰痛,筋骨无力,妊娠漏血,胎动不安,高血压症" }, { "usage", "煎服" }, { "dosage", "6-10g" }, { "contraindication", "阴虚火旺者慎用" }, { "notes", "" }, { "quantity", 320m }, { "unit", "g" }, { "price", 48m }, { "min_stock", 32m } },
                new Dictionary<string, object> { { "name", "牛膝" }, { "alias", "怀牛膝、牛髁膝" }, { "category", "活血化瘀药" }, { "nature", "平" }, { "taste", "苦、甘、酸" }, { "meridian", "归肝、肾经" }, { "efficacy", "逐瘀通经,补肝肾,强筋骨,利尿通淋,引血下行" }, { "indications", "经闭,痛经,腰膝酸痛,筋骨无力,淋证,水肿,头痛,眩晕,牙痛,口疮,吐血,衄血" }, { "usage", "煎服" }, { "dosage", "5-15g" }, { "contraindication", "孕妇慎用" }, { "notes", "" }, { "quantity", 350m }, { "unit", "g" }, { "price", 38m }, { "min_stock", 35m } },
                new Dictionary<string, object> { { "name", "麦冬" }, { "alias", "麦门冬、沿阶草" }, { "category", "补虚药" }, { "nature", "微寒" }, { "taste", "甘、微苦" }, { "meridian", "归心、肺、胃经" }, { "efficacy", "养阴生津,润肺清心" }, { "indications", "肺燥干咳,阴虚痨嗽,喉痹咽痛,津伤口渴,内热消渴,心烦失眠,肠燥便秘" }, { "usage", "煎服" }, { "dosage", "6-12g" }, { "contraindication", "脾胃虚寒泄泻者慎用" }, { "notes", "" }, { "quantity", 380m }, { "unit", "g" }, { "price", 45m }, { "min_stock", 38m } },
                new Dictionary<string, object> { { "name", "五味子" }, { "alias", "玄及、会及" }, { "category", "收涩药" }, { "nature", "温" }, { "taste", "酸、甘" }, { "meridian", "归肺、心、肾经" }, { "efficacy", "收敛固涩,益气生津,补肾宁心" }, { "indications", "久嗽虚喘,梦遗滑精,遗尿尿频,久泻不止,自汗盗汗,津伤口渴,内热消渴,心悸失眠" }, { "usage", "煎服" }, { "dosage", "2-6g" }, { "contraindication", "外有表邪,内有实热,或咳嗽初起、麻疹初发者慎用" }, { "notes", "" }, { "quantity", 250m }, { "unit", "g" }, { "price", 55m }, { "min_stock", 25m } },
                new Dictionary<string, object> { { "name", "大黄" }, { "alias", "将军、锦纹" }, { "category", "泻下药" }, { "nature", "寒" }, { "taste", "苦" }, { "meridian", "归脾、胃、大肠、肝、心包经" }, { "efficacy", "泻下攻积,清热泻火,凉血解毒,逐瘀通经,利湿退黄" }, { "indications", "实热积滞便秘,血热吐衄,目赤咽肿,痈肿疔疮,肠痈腹痛,瘀血经闭,产后瘀阻,跌打损伤,湿热痢疾,黄疸尿赤" }, { "usage", "煎服" }, { "dosage", "3-15g" }, { "contraindication", "孕妇及月经期、哺乳期慎用" }, { "notes", "后下泻下力强" }, { "quantity", 280m }, { "unit", "g" }, { "price", 32m }, { "min_stock", 28m } },
            };
        }
    }
}
