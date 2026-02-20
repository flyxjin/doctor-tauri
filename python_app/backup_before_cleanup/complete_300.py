import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

new_medicines = [
    {"name": "鹿茸", "alias": "斑龙珠", "category": "补虚药", "nature": "温", "taste": "甘、咸", "meridian": "归肾、肝经", "efficacy": "壮肾阳，益精血，强筋骨，调冲任，托疮毒", "indications": "肾阳不足，精血亏虚，阳痿滑精，宫冷不孕，羸瘦，神疲，畏寒，眩晕耳鸣，腰膝酸软，筋骨痿软，崩漏带下，阴疽不敛", "usage": "研末冲服", "dosage": "1-2g", "contraindication": "阴虚阳亢者忌服", "quantity": 50, "unit": "g", "price": 380, "min_stock": 10},
    {"name": "紫河车", "alias": "胎盘", "category": "补虚药", "nature": "温", "taste": "甘、咸", "meridian": "归肺、肝、肾经", "efficacy": "温肾补精，益气养血", "indications": "虚劳羸瘦，骨蒸盗汗，咳嗽气喘，食少气短，阳痿遗精，不孕少乳", "usage": "研末服", "dosage": "2-3g", "contraindication": "阴虚火旺者不宜单独应用", "quantity": 30, "unit": "g", "price": 280, "min_stock": 8},
    {"name": "淫羊藿", "alias": "仙灵脾", "category": "补虚药", "nature": "温", "taste": "辛、甘", "meridian": "归肝、肾经", "efficacy": "补肾阳，强筋骨，祛风湿", "indications": "肾阳虚衰，阳痿遗精，筋骨痿软，风湿痹痛，麻木拘挛", "usage": "煎服", "dosage": "6-10g", "contraindication": "阴虚火旺者不宜服", "quantity": 320, "unit": "g", "price": 35, "min_stock": 38},
    {"name": "巴戟天", "alias": "巴戟", "category": "补虚药", "nature": "微温", "taste": "辛、甘", "meridian": "归肾、肝经", "efficacy": "补肾阳，强筋骨，祛风湿", "indications": "阳痿遗精，宫冷不孕，月经不调，少腹冷痛，风湿痹痛，筋骨痿软", "usage": "煎服", "dosage": "3-10g", "contraindication": "阴虚火旺者忌服", "quantity": 280, "unit": "g", "price": 42, "min_stock": 32},
    {"name": "仙茅", "alias": "独茅根", "category": "补虚药", "nature": "热", "taste": "辛", "meridian": "归肾、肝、脾经", "efficacy": "补肾阳，强筋骨，祛寒湿", "indications": "阳痿精冷，筋骨痿软，腰膝冷痛，阳虚冷泻", "usage": "煎服", "dosage": "3-10g", "contraindication": "阴虚火旺者忌服", "quantity": 200, "unit": "g", "price": 48, "min_stock": 25},
    {"name": "杜仲", "alias": "木棉", "category": "补虚药", "nature": "温", "taste": "甘", "meridian": "归肝、肾经", "efficacy": "补肝肾，强筋骨，安胎", "indications": "肝肾不足，腰膝酸痛，筋骨无力，头晕目眩，妊娠漏血，胎动不安", "usage": "煎服", "dosage": "6-10g", "contraindication": "阴虚火旺者慎服", "quantity": 350, "unit": "g", "price": 38, "min_stock": 40},
    {"name": "续断", "alias": "川断", "category": "补虚药", "nature": "微温", "taste": "苦、辛", "meridian": "归肝、肾经", "efficacy": "补肝肾，强筋骨，续折伤，止崩漏", "indications": "肝肾不足，腰膝酸软，风湿痹痛，跌扑损伤，筋伤骨折，崩漏，胎漏", "usage": "煎服", "dosage": "9-15g", "contraindication": "风湿热痹者慎服", "quantity": 300, "unit": "g", "price": 32, "min_stock": 35},
    {"name": "肉苁蓉", "alias": "大芸", "category": "补虚药", "nature": "温", "taste": "甘、咸", "meridian": "归肾、大肠经", "efficacy": "补肾阳，益精血，润肠通便", "indications": "肾阳不足，精血亏虚，阳痿不孕，腰膝酸软，筋骨无力，肠燥便秘", "usage": "煎服", "dosage": "6-10g", "contraindication": "阴虚火旺及大便泄泻者忌服", "quantity": 250, "unit": "g", "price": 85, "min_stock": 28},
    {"name": "锁阳", "alias": "不老药", "category": "补虚药", "nature": "温", "taste": "甘", "meridian": "归肝、肾、大肠经", "efficacy": "补肾阳，益精血，润肠通便", "indications": "肾阳不足，精血亏虚，腰膝痿软，阳痿滑精，肠燥便秘", "usage": "煎服", "dosage": "5-10g", "contraindication": "阴虚火旺，脾虚泄泻及实热便秘者禁服", "quantity": 220, "unit": "g", "price": 65, "min_stock": 26},
    {"name": "补骨脂", "alias": "破故纸", "category": "补虚药", "nature": "温", "taste": "辛、苦", "meridian": "归肾、脾经", "efficacy": "温肾助阳，纳气平喘，温脾止泻", "indications": "肾阳不足，阳痿遗精，遗尿尿频，腰膝冷痛，肾虚作喘，五更泄泻", "usage": "煎服", "dosage": "6-10g", "contraindication": "阴虚火旺者忌服", "quantity": 280, "unit": "g", "price": 35, "min_stock": 32},
    {"name": "益智仁", "alias": "益智子", "category": "补虚药", "nature": "温", "taste": "辛", "meridian": "归脾、肾经", "efficacy": "暖肾固精缩尿，温脾开胃摄唾", "indications": "肾虚遗尿，小便频数，遗精白浊，脾寒泄泻，腹中冷痛，口多唾涎", "usage": "煎服", "dosage": "3-10g", "contraindication": "阴虚火旺者忌服", "quantity": 260, "unit": "g", "price": 42, "min_stock": 30},
    {"name": "菟丝子", "alias": "吐丝子", "category": "补虚药", "nature": "平", "taste": "辛、甘", "meridian": "归肝、肾、脾经", "efficacy": "补益肝肾，固精缩尿，安胎，明目，止泻", "indications": "肝肾不足，腰膝酸软，阳痿遗精，遗尿尿频，肾虚胎漏，胎动不安，目昏耳鸣，脾肾虚泻", "usage": "煎服", "dosage": "6-12g", "contraindication": "阴虚火旺，大便燥结，小便短赤者不宜服", "quantity": 320, "unit": "g", "price": 28, "min_stock": 38},
    {"name": "沙苑子", "alias": "潼蒺藜", "category": "补虚药", "nature": "温", "taste": "甘", "meridian": "归肝、肾经", "efficacy": "补肾助阳，固精缩尿，养肝明目", "indications": "肾虚腰痛，遗精早泄，遗尿尿频，白浊带下，眩晕，目暗昏花", "usage": "煎服", "dosage": "9-15g", "contraindication": "阴虚火旺及小便不利者忌服", "quantity": 240, "unit": "g", "price": 38, "min_stock": 28},
    {"name": "蛤蚧", "alias": "大壁虎", "category": "补虚药", "nature": "平", "taste": "咸", "meridian": "归肺、肾经", "efficacy": "补肺益肾，纳气定喘，助阳益精", "indications": "肺肾不足，虚喘气促，劳嗽咳血，阳痿，遗精", "usage": "研末服", "dosage": "3-6g", "contraindication": "风寒或实热咳嗽忌服", "quantity": 40, "unit": "g", "price": 180, "min_stock": 10},
    {"name": "核桃仁", "alias": "胡桃肉", "category": "补虚药", "nature": "温", "taste": "甘", "meridian": "归肾、肺、大肠经", "efficacy": "补肾温肺，润肠通便", "indications": "肾阳不足，腰膝酸软，阳痿遗精，虚寒喘嗽，肠燥便秘", "usage": "煎服", "dosage": "6-9g", "contraindication": "阴虚火旺，痰热咳嗽及便溏者不宜服", "quantity": 400, "unit": "g", "price": 45, "min_stock": 45},
    {"name": "冬虫夏草", "alias": "虫草", "category": "补虚药", "nature": "平", "taste": "甘", "meridian": "归肺、肾经", "efficacy": "补肾益肺，止血化痰", "indications": "肾虚精亏，阳痿遗精，腰膝酸痛，久咳虚喘，劳嗽咯血", "usage": "煎服或研末服", "dosage": "3-9g", "contraindication": "有表邪者慎用", "quantity": 20, "unit": "g", "price": 380, "min_stock": 5},
    {"name": "胡芦巴", "alias": "芦巴子", "category": "补虚药", "nature": "温", "taste": "苦", "meridian": "归肾经", "efficacy": "温肾助阳，祛寒止痛", "indications": "肾脏虚冷，腹胁胀满，寒湿脚气，寒疝腹痛，阳痿", "usage": "煎服", "dosage": "3-10g", "contraindication": "阴虚火旺者忌服", "quantity": 180, "unit": "g", "price": 32, "min_stock": 22},
    {"name": "韭菜子", "alias": "韭子", "category": "补虚药", "nature": "温", "taste": "辛、甘", "meridian": "归肝、肾经", "efficacy": "温补肝肾，壮阳固精", "indications": "肝肾不足，肾阳虚衰，阳痿遗精，腰膝酸软，遗尿尿频，白浊带下", "usage": "煎服", "dosage": "3-9g", "contraindication": "阴虚火旺者忌服", "quantity": 200, "unit": "g", "price": 28, "min_stock": 25},
    {"name": "阳起石", "alias": "白石", "category": "补虚药", "nature": "温", "taste": "咸", "meridian": "归肾经", "efficacy": "温肾壮阳", "indications": "肾阳虚衰，阳痿宫冷，腰膝酸软", "usage": "煎服", "dosage": "3-6g", "contraindication": "阴虚火旺者忌服，不宜久服", "quantity": 150, "unit": "g", "price": 25, "min_stock": 18},
    {"name": "紫石英", "alias": "萤石", "category": "补虚药", "nature": "温", "taste": "甘", "meridian": "归心、肺、肾经", "efficacy": "温肾暖宫，镇心安神，温肺平喘", "indications": "肾阳不足，宫冷不孕，惊悸怔忡，虚烦不眠，肺寒气逆，痰多喘咳", "usage": "煎服", "dosage": "9-15g", "contraindication": "阴虚火旺者忌服", "quantity": 180, "unit": "g", "price": 35, "min_stock": 22},
    {"name": "海狗肾", "alias": "腽肭脐", "category": "补虚药", "nature": "热", "taste": "咸", "meridian": "归肝、肾经", "efficacy": "暖肾壮阳，益精补髓", "indications": "肾阳虚衰，阳痿精冷，腰膝痿弱，羸瘦", "usage": "研末服", "dosage": "1-3g", "contraindication": "阴虚火旺者忌服", "quantity": 15, "unit": "g", "price": 280, "min_stock": 5},
    {"name": "海马", "alias": "水马", "category": "补虚药", "nature": "温", "taste": "甘、咸", "meridian": "归肝、肾经", "efficacy": "温肾壮阳，散结消肿", "indications": "肾阳虚衰，阳痿宫冷，遗尿尿频，肾虚作喘，癥瘕积聚，跌扑损伤，痈肿疔疮", "usage": "研末服", "dosage": "1-3g", "contraindication": "阴虚火旺者忌服", "quantity": 25, "unit": "g", "price": 320, "min_stock": 8},
    {"name": "阿胶", "alias": "驴皮胶", "category": "补虚药", "nature": "平", "taste": "甘", "meridian": "归肺、肝、肾经", "efficacy": "补血滋阴，润燥，止血", "indications": "血虚萎黄，眩晕心悸，肌痿无力，心烦不眠，虚风内动，肺燥咳嗽，劳嗽咯血，吐血尿血，便血崩漏，妊娠胎漏", "usage": "烊化兑服", "dosage": "3-9g", "contraindication": "脾胃虚弱者慎服", "quantity": 120, "unit": "g", "price": 180, "min_stock": 15},
    {"name": "何首乌", "alias": "首乌", "category": "补虚药", "nature": "微温", "taste": "苦、甘、涩", "meridian": "归肝、心、肾经", "efficacy": "制用：补肝肾，益精血，乌须发；生用：解毒，截疟，润肠通便", "indications": "血虚萎黄，眩晕耳鸣，须发早白，腰膝酸软，肢体麻木，崩漏带下，体虚久疟，肠燥便秘，痈疽瘰疬", "usage": "煎服", "dosage": "6-12g", "contraindication": "大便溏泄及湿痰较重者不宜服", "quantity": 280, "unit": "g", "price": 48, "min_stock": 32},
    {"name": "龙眼肉", "alias": "桂圆肉", "category": "补虚药", "nature": "温", "taste": "甘", "meridian": "归心、脾经", "efficacy": "补益心脾，养血安神", "indications": "气血不足，心悸怔忡，健忘失眠，血虚萎黄", "usage": "煎服", "dosage": "9-15g", "contraindication": "内有痰火及湿滞停饮者忌服", "quantity": 350, "unit": "g", "price": 42, "min_stock": 40},
    {"name": "楮实子", "alias": "楮实", "category": "补虚药", "nature": "寒", "taste": "甘", "meridian": "归肝、肾经", "efficacy": "滋肾，清肝，明目，利尿", "indications": "肝肾阴虚，目生翳障，目昏不明，水肿胀满", "usage": "煎服", "dosage": "6-9g", "contraindication": "脾胃虚寒者慎服", "quantity": 180, "unit": "g", "price": 28, "min_stock": 22},
    {"name": "北沙参", "alias": "辽沙参", "category": "补虚药", "nature": "微寒", "taste": "甘、微苦", "meridian": "归肺、胃经", "efficacy": "养阴清肺，益胃生津", "indications": "肺热燥咳，劳嗽痰血，胃阴不足，热病津伤，咽干口渴", "usage": "煎服", "dosage": "5-12g", "contraindication": "风寒咳嗽及肺胃虚寒者忌服", "quantity": 280, "unit": "g", "price": 55, "min_stock": 32},
    {"name": "西洋参", "alias": "花旗参", "category": "补虚药", "nature": "凉", "taste": "甘、微苦", "meridian": "归心、肺、肾经", "efficacy": "补气养阴，清热生津", "indications": "气虚阴亏，虚热烦倦，咳喘痰血，内热消渴，口燥咽干", "usage": "煎服", "dosage": "3-6g", "contraindication": "中阳衰微，胃有寒湿者忌服", "quantity": 150, "unit": "g", "price": 280, "min_stock": 18},
    {"name": "太子参", "alias": "孩儿参", "category": "补虚药", "nature": "平", "taste": "甘、微苦", "meridian": "归脾、肺经", "efficacy": "益气健脾，生津润肺", "indications": "脾虚体倦，食欲不振，病后虚弱，气阴不足，自汗口渴，肺燥干咳", "usage": "煎服", "dosage": "9-30g", "contraindication": "邪实而正气不虚者慎用", "quantity": 300, "unit": "g", "price": 65, "min_stock": 35},
    {"name": "山药", "alias": "薯蓣", "category": "补虚药", "nature": "平", "taste": "甘", "meridian": "归脾、肺、肾经", "efficacy": "补脾养胃，生津益肺，补肾涩精", "indications": "脾虚食少，久泻不止，肺虚喘咳，肾虚遗精，带下，尿频，虚热消渴", "usage": "煎服", "dosage": "15-30g", "contraindication": "湿盛中满或有实邪、积滞者禁服", "quantity": 450, "unit": "g", "price": 28, "min_stock": 50},
    {"name": "白扁豆", "alias": "藊豆", "category": "补虚药", "nature": "微温", "taste": "甘", "meridian": "归脾、胃经", "efficacy": "健脾化湿，和中消暑", "indications": "脾胃虚弱，食欲不振，大便溏泻，白带过多，暑湿吐泻，胸闷腹胀", "usage": "煎服", "dosage": "9-15g", "contraindication": "多食壅气，伤寒邪炽者禁用", "quantity": 350, "unit": "g", "price": 22, "min_stock": 40},
    {"name": "大枣", "alias": "红枣", "category": "补虚药", "nature": "温", "taste": "甘", "meridian": "归脾、胃、心经", "efficacy": "补中益气，养血安神", "indications": "脾虚食少，乏力便溏，妇人脏躁", "usage": "煎服", "dosage": "6-15g", "contraindication": "凡湿盛、痰凝、食滞、虫积及齿病者，慎服或禁服", "quantity": 500, "unit": "g", "price": 18, "min_stock": 55},
    {"name": "蜂蜜", "alias": "白蜜", "category": "补虚药", "nature": "平", "taste": "甘", "meridian": "归肺、脾、大肠经", "efficacy": "补中，润燥，止痛，解毒；外用生肌敛疮", "indications": "脘腹虚痛，肺燥干咳，肠燥便秘，解乌头类药毒；外治疮疡不敛，水火烫伤", "usage": "煎服或冲服", "dosage": "15-30g", "contraindication": "湿热痰滞，胸闷不宽及便溏或泄泻者慎用", "quantity": 400, "unit": "g", "price": 45, "min_stock": 45},
    {"name": "饴糖", "alias": "麦芽糖", "category": "补虚药", "nature": "温", "taste": "甘", "meridian": "归脾、胃、肺经", "efficacy": "补中缓急，润肺止咳，解毒", "indications": "脾胃虚寒，里急腹痛，肺燥咳嗽，咽痛，吐血，口渴，咽痛，便秘", "usage": "烊化冲服", "dosage": "15-20g", "contraindication": "湿热内郁，中满吐逆者忌服", "quantity": 200, "unit": "g", "price": 32, "min_stock": 25},
    {"name": "红景天", "alias": "扫罗玛尔布", "category": "补虚药", "nature": "寒", "taste": "甘、苦", "meridian": "归肺、心经", "efficacy": "益气活血，通脉平喘", "indications": "气虚血瘀，胸痹心痛，中风偏瘫，倦怠气喘", "usage": "煎服", "dosage": "3-6g", "contraindication": "儿童、孕妇慎用", "quantity": 180, "unit": "g", "price": 85, "min_stock": 22},
    {"name": "刺五加", "alias": "五加皮", "category": "补虚药", "nature": "温", "taste": "辛、微苦", "meridian": "归脾、肾、心经", "efficacy": "益气健脾，补肾安神", "indications": "脾肾阳虚，体虚乏力，食欲不振，腰膝酸痛，失眠多梦", "usage": "煎服", "dosage": "9-27g", "contraindication": "阴虚火旺者慎服", "quantity": 250, "unit": "g", "price": 38, "min_stock": 30},
    {"name": "绞股蓝", "alias": "七叶胆", "category": "补虚药", "nature": "寒", "taste": "苦、甘", "meridian": "归肺、脾、肾经", "efficacy": "益气健脾，化痰止咳，清热解毒", "indications": "脾虚乏力，虚劳失精，白细胞减少症，高脂血症，病毒性肝炎，慢性胃肠炎，慢性气管炎", "usage": "煎服", "dosage": "15-30g", "contraindication": "虚寒证忌用", "quantity": 280, "unit": "g", "price": 32, "min_stock": 32},
    {"name": "沙棘", "alias": "醋柳果", "category": "补虚药", "nature": "温", "taste": "酸、涩", "meridian": "归脾、胃、肺、心经", "efficacy": "健脾消食，止咳祛痰，活血散瘀", "indications": "脾虚食少，食积腹痛，咳嗽痰多，胸痹心痛，瘀血经闭，跌扑瘀肿", "usage": "煎服", "dosage": "3-10g", "contraindication": "胃酸过多者慎服", "quantity": 180, "unit": "g", "price": 55, "min_stock": 22},
    {"name": "牛蒡子", "alias": "大力子", "category": "解表药", "nature": "寒", "taste": "辛、苦", "meridian": "归肺、胃经", "efficacy": "疏散风热，宣肺透疹，解毒利咽", "indications": "风热感冒，咳嗽痰多，麻疹，风疹，咽喉肿痛，痄腮，丹毒，痈肿疮毒", "usage": "煎服", "dosage": "6-12g", "contraindication": "气虚便溏者慎用", "quantity": 320, "unit": "g", "price": 28, "min_stock": 38},
    {"name": "蝉蜕", "alias": "蝉衣", "category": "解表药", "nature": "寒", "taste": "甘", "meridian": "归肺、肝经", "efficacy": "疏散风热，利咽，透疹，明目退翳，解痉", "indications": "风热感冒，咽痛音哑，麻疹不透，风疹瘙痒，目赤翳障，惊风抽搐，破伤风", "usage": "煎服", "dosage": "3-6g", "contraindication": "孕妇慎用", "quantity": 250, "unit": "g", "price": 75, "min_stock": 28},
    {"name": "桑叶", "alias": "家桑", "category": "解表药", "nature": "寒", "taste": "甘、苦", "meridian": "归肺、肝经", "efficacy": "疏散风热，清肺润燥，清肝明目", "indications": "风热感冒，肺热燥咳，头晕头痛，目赤昏花", "usage": "煎服", "dosage": "5-10g", "contraindication": "脾胃虚寒者慎服", "quantity": 380, "unit": "g", "price": 18, "min_stock": 45},
    {"name": "蔓荆子", "alias": "万荆子", "category": "解表药", "nature": "微寒", "taste": "辛、苦", "meridian": "归膀胱、肝、胃经", "efficacy": "疏散风热，清利头目", "indications": "风热感冒头痛，齿龈肿痛，目赤多泪，目暗不明，头晕目眩", "usage": "煎服", "dosage": "5-10g", "contraindication": "血虚有火之头痛目眩及胃虚者慎服", "quantity": 240, "unit": "g", "price": 42, "min_stock": 28},
    {"name": "升麻", "alias": "周升麻", "category": "解表药", "nature": "微寒", "taste": "辛、微甘", "meridian": "归肺、脾、胃、大肠经", "efficacy": "发表透疹，清热解毒，升举阳气", "indications": "风热头痛，齿痛，口疮，咽喉肿痛，麻疹不透，阳毒发斑，脱肛，子宫脱垂", "usage": "煎服", "dosage": "3-10g", "contraindication": "麻疹已透，阴虚火旺，以及阴虚阳亢者，均当忌用", "quantity": 280, "unit": "g", "price": 35, "min_stock": 32},
    {"name": "生地黄", "alias": "生地", "category": "清热药", "nature": "寒", "taste": "甘、苦", "meridian": "归心、肝、肾经", "efficacy": "清热凉血，养阴生津", "indications": "热入营血，温毒发斑，吐血衄血，热病伤阴，舌绛烦渴，津伤便秘，阴虚发热，骨蒸劳热，内热消渴", "usage": "煎服", "dosage": "10-15g", "contraindication": "脾虚湿滞者忌用", "quantity": 350, "unit": "g", "price": 48, "min_stock": 40},
    {"name": "玄参", "alias": "元参", "category": "清热药", "nature": "微寒", "taste": "甘、苦、咸", "meridian": "归肺、胃、肾经", "efficacy": "清热凉血，滋阴降火，解毒散结", "indications": "热入营血，温毒发斑，热病伤阴，舌绛烦渴，津伤便秘，骨蒸劳嗽，目赤，咽痛，白喉，瘰疬，痈肿疮毒", "usage": "煎服", "dosage": "9-15g", "contraindication": "脾胃虚寒者不宜", "quantity": 300, "unit": "g", "price": 38, "min_stock": 35},
    {"name": "牡丹皮", "alias": "丹皮", "category": "清热药", "nature": "微寒", "taste": "苦、辛", "meridian": "归心、肝、肾经", "efficacy": "清热凉血，活血化瘀", "indications": "热入营血，温毒发斑，吐血衄血，夜热早凉，无汗骨蒸，经闭痛经，跌扑伤痛，痈肿疮毒", "usage": "煎服", "dosage": "6-12g", "contraindication": "血虚有寒者慎用", "quantity": 280, "unit": "g", "price": 52, "min_stock": 32},
    {"name": "赤芍", "alias": "红芍药", "category": "清热药", "nature": "微寒", "taste": "苦", "meridian": "归肝经", "efficacy": "清热凉血，散瘀止痛", "indications": "热入营血，温毒发斑，吐血衄血，目赤肿痛，肝郁胁痛，经闭痛经，癥瘕腹痛，跌扑损伤，痈肿疮疡", "usage": "煎服", "dosage": "6-12g", "contraindication": "血寒经闭者不宜", "quantity": 320, "unit": "g", "price": 32, "min_stock": 38},
    {"name": "青蒿", "alias": "香蒿", "category": "清热药", "nature": "寒", "taste": "苦、辛", "meridian": "归肝、胆经", "efficacy": "清虚热，除骨蒸，解暑热，截疟，退黄", "indications": "温邪伤阴，夜热早凉，阴虚发热，骨蒸劳热，暑邪发热，疟疾寒热，湿热黄疸", "usage": "煎服", "dosage": "6-12g", "contraindication": "脾胃虚弱者慎用", "quantity": 320, "unit": "g", "price": 25, "min_stock": 38},
    {"name": "白薇", "alias": "白龙须", "category": "清热药", "nature": "寒", "taste": "苦、咸", "meridian": "归胃、肝、肾经", "efficacy": "清热凉血，利尿通淋，解毒疗疮", "indications": "温邪伤营发热，阴虚发热，骨蒸劳热，产后血虚发热，热淋，血淋，痈疽肿毒", "usage": "煎服", "dosage": "5-10g", "contraindication": "脾胃虚寒者不宜", "quantity": 240, "unit": "g", "price": 38, "min_stock": 28},
    {"name": "地骨皮", "alias": "杞根皮", "category": "清热药", "nature": "寒", "taste": "甘", "meridian": "归肺、肝、肾经", "efficacy": "凉血除蒸，清肺降火", "indications": "阴虚潮热，骨蒸盗汗，肺热咳嗽，咯血，衄血，内热消渴", "usage": "煎服", "dosage": "9-15g", "contraindication": "脾胃虚寒者忌用", "quantity": 260, "unit": "g", "price": 32, "min_stock": 30},
    {"name": "芒硝", "alias": "朴硝", "category": "泻下药", "nature": "寒", "taste": "咸、苦", "meridian": "归胃、大肠经", "efficacy": "泻下通便，润燥软坚，清火消肿", "indications": "实热积滞，腹满胀痛，大便燥结，肠痈肿痛；外治乳痈，痔疮肿痛", "usage": "冲入药汁内或开水溶化后服", "dosage": "6-12g", "contraindication": "孕妇慎用", "quantity": 250, "unit": "g", "price": 22, "min_stock": 28},
]

def complete_to_300():
    print("=" * 60)
    print("补充药材到300味")
    print("=" * 60)
    
    db = Database()
    
    added = 0
    errors = 0
    
    for medicine in new_medicines:
        try:
            existing = db.fetchone(
                "SELECT id FROM medicines WHERE name = ?", 
                (medicine['name'],)
            )
            
            if not existing:
                print(f"添加: {medicine['name']}...", end="")
                
                db.execute('''
                    INSERT INTO medicines 
                    (name, alias, category, nature, taste, meridian, 
                     efficacy, indications, usage, dosage, contraindication, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    medicine['name'],
                    medicine.get('alias', ''),
                    medicine.get('category', ''),
                    medicine.get('nature', ''),
                    medicine.get('taste', ''),
                    medicine.get('meridian', ''),
                    medicine.get('efficacy', ''),
                    medicine.get('indications', ''),
                    medicine.get('usage', ''),
                    medicine.get('dosage', ''),
                    medicine.get('contraindication', ''),
                    medicine.get('notes', '')
                ))
                
                med_id = db.fetchone(
                    "SELECT id FROM medicines WHERE name = ?", 
                    (medicine['name'],)
                )[0]
                
                db.execute('''
                    INSERT INTO inventory 
                    (medicine_id, quantity, unit, price, min_stock, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    med_id,
                    medicine.get('quantity', 0),
                    medicine.get('unit', 'g'),
                    medicine.get('price', 0),
                    medicine.get('min_stock', 10),
                    medicine.get('notes', '')
                ))
                
                added += 1
                print("成功！")
            else:
                print(f"跳过: {medicine['name']} (已存在)")
                
        except Exception as e:
            errors += 1
            print(f"错误: {medicine['name']} - {str(e)}")
            continue
    
    print("\n" + "=" * 60)
    print("修复缺失的库存记录")
    print("=" * 60)
    
    medicines_without_inventory = db.fetchall('''
        SELECT m.id, m.name FROM medicines m 
        LEFT JOIN inventory i ON m.id = i.medicine_id 
        WHERE i.id IS NULL
    ''')
    
    fixed = 0
    for med_id, med_name in medicines_without_inventory:
        try:
            db.execute('''
                INSERT INTO inventory 
                (medicine_id, quantity, unit, price, min_stock, notes)
                VALUES (?, 100, 'g', 20, 10, '')
            ''', (med_id,))
            fixed += 1
            print(f"为 {med_name} 创建库存记录")
        except Exception as e:
            print(f"创建库存记录失败: {med_name} - {str(e)}")
    
    print("\n" + "=" * 60)
    print("最终统计")
    print("=" * 60)
    
    med_count = db.fetchone("SELECT COUNT(*) FROM medicines")[0]
    inv_count = db.fetchone("SELECT COUNT(*) FROM inventory")[0]
    
    print(f"\n新增药材: {added} 味")
    print(f"修复库存记录: {fixed} 条")
    print(f"错误: {errors}")
    print(f"\n当前药材总数: {med_count}")
    print(f"当前库存记录: {inv_count}")
    
    db.close()

if __name__ == '__main__':
    complete_to_300()
    input("\n按任意键退出...")