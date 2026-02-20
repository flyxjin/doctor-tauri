import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

new_medicines = [
    {"name": "紫草", "alias": "紫丹", "category": "清热药", "nature": "寒", "taste": "甘、咸", "meridian": "归心、肝经", "efficacy": "清热凉血，活血解毒，透疹消斑", "indications": "血热毒盛，斑疹紫黑，麻疹不透，疮疡，湿疹，水火烫伤", "usage": "煎服", "dosage": "5-10g", "contraindication": "脾胃虚寒者慎服", "quantity": 200, "unit": "g", "price": 45, "min_stock": 25},
    {"name": "水牛角", "alias": "牛角", "category": "清热药", "nature": "寒", "taste": "苦、咸", "meridian": "归心、肝经", "efficacy": "清热凉血，解毒，定惊", "indications": "温病高热，神昏谵语，惊风，癫狂，血热妄行斑疹，吐衄，痈肿疮疡", "usage": "镑片或粗粉煎服", "dosage": "15-30g", "contraindication": "脾胃虚寒者慎服", "quantity": 180, "unit": "g", "price": 35, "min_stock": 22},
    {"name": "银柴胡", "alias": "银胡", "category": "清热药", "nature": "微寒", "taste": "甘", "meridian": "归肝、胃经", "efficacy": "清虚热，除疳热，清热凉血", "indications": "阴虚发热，骨蒸劳热，小儿疳热", "usage": "煎服", "dosage": "3-10g", "contraindication": "外感风寒，血虚无热者忌服", "quantity": 220, "unit": "g", "price": 42, "min_stock": 26},
    {"name": "胡黄连", "alias": "胡连", "category": "清热药", "nature": "寒", "taste": "苦", "meridian": "归肝、胃、大肠经", "efficacy": "退虚热，除疳热，清湿热", "indications": "骨蒸潮热，小儿疳热，湿热泻痢，黄疸尿赤，痔疮肿痛", "usage": "煎服", "dosage": "3-10g", "contraindication": "脾胃虚寒者慎服", "quantity": 200, "unit": "g", "price": 48, "min_stock": 24},
    {"name": "番泻叶", "alias": "泻叶", "category": "泻下药", "nature": "寒", "taste": "甘、苦", "meridian": "归大肠经", "efficacy": "泻热行滞，通便，利水", "indications": "热结积滞，便秘腹痛，水肿胀满", "usage": "煎服", "dosage": "2-6g", "contraindication": "孕妇慎用，体虚者忌服", "quantity": 250, "unit": "g", "price": 25, "min_stock": 30},
    {"name": "芦荟", "alias": "卢会", "category": "泻下药", "nature": "寒", "taste": "苦", "meridian": "归肝、胃、大肠经", "efficacy": "清肝热，通便，杀虫疗疳", "indications": "便秘，小儿疳积，惊风，外治湿癣", "usage": "入丸散服", "dosage": "2-5g", "contraindication": "脾胃虚寒，食少便溏及孕妇忌服", "quantity": 180, "unit": "g", "price": 38, "min_stock": 22},
    {"name": "火麻仁", "alias": "麻子仁", "category": "泻下药", "nature": "平", "taste": "甘", "meridian": "归脾、胃、大肠经", "efficacy": "润肠通便", "indications": "血虚津亏，肠燥便秘", "usage": "煎服", "dosage": "10-15g", "contraindication": "脾肾不足之便溏、阳痿、遗精、带下者慎服", "quantity": 320, "unit": "g", "price": 22, "min_stock": 38},
    {"name": "郁李仁", "alias": "小李仁", "category": "泻下药", "nature": "平", "taste": "辛、苦、甘", "meridian": "归脾、大肠、小肠经", "efficacy": "润燥滑肠，下气利水", "indications": "津枯肠燥，食积气滞，腹胀便秘，水肿，脚气，小便不利", "usage": "煎服", "dosage": "6-10g", "contraindication": "孕妇慎服", "quantity": 200, "unit": "g", "price": 35, "min_stock": 24},
    {"name": "松子仁", "alias": "松子", "category": "泻下药", "nature": "温", "taste": "甘", "meridian": "归肺、肝、大肠经", "efficacy": "润肠通便，润肺止咳", "indications": "肠燥便秘，肺燥干咳", "usage": "煎服", "dosage": "5-10g", "contraindication": "脾虚便溏，湿痰者禁服", "quantity": 280, "unit": "g", "price": 42, "min_stock": 32},
    {"name": "甘遂", "alias": "甘泽", "category": "泻下药", "nature": "寒", "taste": "苦", "meridian": "归肺、肾、大肠经", "efficacy": "泻水逐饮，消肿散结", "indications": "水肿胀满，胸腹积水，痰饮积聚，气逆喘咳，二便不利，风痰癫痫，痈肿疮毒", "usage": "入丸散服", "dosage": "0.5-1.5g", "contraindication": "孕妇禁用，不宜与甘草同用", "quantity": 80, "unit": "g", "price": 45, "min_stock": 10},
    {"name": "京大戟", "alias": "大戟", "category": "泻下药", "nature": "寒", "taste": "苦", "meridian": "归肺、脾、肾经", "efficacy": "泻水逐饮，消肿散结", "indications": "水肿胀满，胸腹积水，痰饮积聚，痈肿瘰疬", "usage": "煎服", "dosage": "1.5-3g", "contraindication": "孕妇禁用，不宜与甘草同用", "quantity": 100, "unit": "g", "price": 38, "min_stock": 12},
    {"name": "芫花", "alias": "赤芫", "category": "泻下药", "nature": "温", "taste": "苦、辛", "meridian": "归肺、脾、肾经", "efficacy": "泻水逐饮，祛痰止咳，外用杀虫疗疮", "indications": "水肿胀满，胸腹积水，痰饮积聚，气逆喘咳，二便不利，疥癣秃疮，冻疮", "usage": "煎服", "dosage": "1.5-3g", "contraindication": "孕妇禁用，不宜与甘草同用", "quantity": 100, "unit": "g", "price": 35, "min_stock": 12},
    {"name": "商陆", "alias": "章陆", "category": "泻下药", "nature": "寒", "taste": "苦", "meridian": "归肺、脾、肾、大肠经", "efficacy": "逐水消肿，通利二便，外用解毒散结", "indications": "水肿胀满，二便不利，痈肿疮毒", "usage": "煎服", "dosage": "3-9g", "contraindication": "孕妇禁用", "quantity": 150, "unit": "g", "price": 28, "min_stock": 18},
    {"name": "牵牛子", "alias": "二丑", "category": "泻下药", "nature": "寒", "taste": "苦", "meridian": "归肺、肾、大肠经", "efficacy": "泻水通便，消痰涤饮，杀虫攻积", "indications": "水肿胀满，二便不通，痰饮积聚，气逆喘咳，虫积腹痛", "usage": "煎服", "dosage": "3-6g", "contraindication": "孕妇禁用，胃弱气虚者慎服", "quantity": 180, "unit": "g", "price": 22, "min_stock": 22},
    {"name": "巴豆霜", "alias": "巴豆", "category": "泻下药", "nature": "热", "taste": "辛", "meridian": "归胃、大肠经", "efficacy": "峻下冷积，逐水退肿，祛痰利咽，外用蚀疮", "indications": "寒积便秘，乳食停滞，腹水鼓胀，二便不通，喉风，喉痹，痈肿脓成未溃，疥癣恶疮", "usage": "入丸散服", "dosage": "0.1-0.3g", "contraindication": "孕妇禁用，不宜与牵牛子同用", "quantity": 30, "unit": "g", "price": 55, "min_stock": 8},
    {"name": "千金子", "alias": "续随子", "category": "泻下药", "nature": "温", "taste": "辛", "meridian": "归肝、肾、大肠经", "efficacy": "泻下逐水，破血消癥，外用疗癣蚀疣", "indications": "二便不通，水肿，痰饮，积滞胀满，血瘀经闭，外治顽癣，赘疣", "usage": "去壳去油用，入丸散服", "dosage": "1-2g", "contraindication": "孕妇禁用，体弱便溏者忌服", "quantity": 50, "unit": "g", "price": 48, "min_stock": 10},
    {"name": "独活", "alias": "独摇草", "category": "祛风湿药", "nature": "微温", "taste": "辛、苦", "meridian": "归肾、膀胱经", "efficacy": "祛风除湿，通痹止痛", "indications": "风寒湿痹，腰膝疼痛，少阴伏风头痛，风寒挟湿头痛", "usage": "煎服", "dosage": "3-10g", "contraindication": "阴虚血燥者慎服", "quantity": 280, "unit": "g", "price": 35, "min_stock": 32},
    {"name": "威灵仙", "alias": "铁脚威灵仙", "category": "祛风湿药", "nature": "温", "taste": "辛、咸", "meridian": "归膀胱经", "efficacy": "祛风湿，通经络，止痛，消骨骾", "indications": "风湿痹痛，肢体麻木，筋脉拘挛，屈伸不利，骨鲠咽喉", "usage": "煎服", "dosage": "6-10g", "contraindication": "气血亏虚及孕妇慎服", "quantity": 260, "unit": "g", "price": 28, "min_stock": 30},
    {"name": "川乌", "alias": "川乌头", "category": "祛风湿药", "nature": "热", "taste": "辛、苦", "meridian": "归心、肝、肾、脾经", "efficacy": "祛风除湿，温经止痛", "indications": "风寒湿痹，关节疼痛，心腹冷痛，寒疝作痛，麻醉止痛", "usage": "先煎、久煎", "dosage": "1.5-3g", "contraindication": "孕妇忌服，不宜与贝母类、半夏、白及、白蔹、天花粉、瓜蒌类同用", "quantity": 100, "unit": "g", "price": 45, "min_stock": 12},
    {"name": "草乌", "alias": "草乌头", "category": "祛风湿药", "nature": "热", "taste": "辛、苦", "meridian": "归心、肝、肾、脾经", "efficacy": "祛风除湿，温经止痛", "indications": "风寒湿痹，关节疼痛，心腹冷痛，寒疝作痛，麻醉止痛", "usage": "先煎、久煎", "dosage": "1.5-3g", "contraindication": "孕妇忌服，不宜与贝母类、半夏、白及、白蔹、天花粉、瓜蒌类同用", "quantity": 100, "unit": "g", "price": 42, "min_stock": 12},
    {"name": "蕲蛇", "alias": "五步蛇", "category": "祛风湿药", "nature": "温", "taste": "甘、咸", "meridian": "归肝经", "efficacy": "祛风，通络，止痉", "indications": "风湿顽痹，麻木拘挛，中风口眼歪斜，半身不遂，抽搐痉挛，破伤风，麻风，疥癣", "usage": "煎服或研末服", "dosage": "3-9g", "contraindication": "血虚生风者慎服", "quantity": 50, "unit": "g", "price": 180, "min_stock": 10},
    {"name": "乌梢蛇", "alias": "乌蛇", "category": "祛风湿药", "nature": "平", "taste": "甘", "meridian": "归肝经", "efficacy": "祛风，通络，止痉", "indications": "风湿顽痹，麻木拘挛，中风口眼歪斜，半身不遂，抽搐痉挛，破伤风，麻风，疥癣，瘰疬恶疮", "usage": "煎服或研末服", "dosage": "6-12g", "contraindication": "血虚生风者慎服", "quantity": 80, "unit": "g", "price": 120, "min_stock": 15},
    {"name": "木瓜", "alias": "贴梗海棠", "category": "祛风湿药", "nature": "温", "taste": "酸", "meridian": "归肝、脾经", "efficacy": "舒筋活络，和胃化湿", "indications": "湿痹拘挛，腰膝关节酸重疼痛，暑湿吐泻，转筋挛痛，脚气水肿", "usage": "煎服", "dosage": "6-9g", "contraindication": "内有郁热，小便短赤者忌服", "quantity": 320, "unit": "g", "price": 25, "min_stock": 38},
    {"name": "蚕沙", "alias": "蚕矢", "category": "祛风湿药", "nature": "温", "taste": "甘、辛", "meridian": "归肝、脾、胃经", "efficacy": "祛风湿，和中化湿", "indications": "风湿痹痛，肢体不遂，风疹瘙痒，吐泻转筋", "usage": "煎服", "dosage": "5-15g", "contraindication": "血虚手足不遂者禁服", "quantity": 200, "unit": "g", "price": 22, "min_stock": 24},
    {"name": "伸筋草", "alias": "石松", "category": "祛风湿药", "nature": "温", "taste": "微苦、辛", "meridian": "归肝、脾、肾经", "efficacy": "祛风除湿，舒筋活络", "indications": "关节酸痛，屈伸不利", "usage": "煎服", "dosage": "3-12g", "contraindication": "孕妇慎用", "quantity": 250, "unit": "g", "price": 18, "min_stock": 30},
    {"name": "寻骨风", "alias": "猫耳朵草", "category": "祛风湿药", "nature": "平", "taste": "辛、苦", "meridian": "归肝经", "efficacy": "祛风湿，通络止痛", "indications": "风湿痹痛，肢体麻木，筋骨拘挛，跌打损伤疼痛", "usage": "煎服", "dosage": "10-15g", "contraindication": "阴虚内热者忌服", "quantity": 180, "unit": "g", "price": 25, "min_stock": 22},
    {"name": "松节", "alias": "油松节", "category": "祛风湿药", "nature": "温", "taste": "苦、辛", "meridian": "归肝、肾经", "efficacy": "祛风除湿，通络止痛", "indications": "风寒湿痹，历节风痛，转筋挛急，跌打伤痛", "usage": "煎服", "dosage": "9-15g", "contraindication": "阴虚血燥者慎服", "quantity": 200, "unit": "g", "price": 15, "min_stock": 24},
    {"name": "海风藤", "alias": "风藤", "category": "祛风湿药", "nature": "微温", "taste": "辛、苦", "meridian": "归肝经", "efficacy": "祛风湿，通经络，止痹痛", "indications": "风寒湿痹，肢节疼痛，筋脉拘挛，屈伸不利", "usage": "煎服", "dosage": "6-12g", "contraindication": "孕妇慎用", "quantity": 220, "unit": "g", "price": 28, "min_stock": 26},
    {"name": "青风藤", "alias": "清风藤", "category": "祛风湿药", "nature": "平", "taste": "苦、辛", "meridian": "归肝、脾经", "efficacy": "祛风湿，通经络，利小便", "indications": "风湿痹痛，关节肿胀，麻痹瘙痒", "usage": "煎服", "dosage": "6-12g", "contraindication": "脾胃虚寒者慎服", "quantity": 200, "unit": "g", "price": 32, "min_stock": 24},
    {"name": "丁公藤", "alias": "麻辣子", "category": "祛风湿药", "nature": "温", "taste": "辛", "meridian": "归肝、脾、胃经", "efficacy": "祛风除湿，消肿止痛", "indications": "风湿痹痛，半身不遂，跌扑肿痛", "usage": "煎服", "dosage": "3-6g", "contraindication": "孕妇忌服", "quantity": 150, "unit": "g", "price": 38, "min_stock": 18},
    {"name": "秦艽", "alias": "大艽", "category": "祛风湿药", "nature": "平", "taste": "辛、苦", "meridian": "归胃、肝、胆经", "efficacy": "祛风湿，清湿热，止痹痛，退虚热", "indications": "风湿痹痛，筋脉拘挛，骨节酸痛，日晡潮热，小儿疳积发热", "usage": "煎服", "dosage": "3-10g", "contraindication": "久病虚寒，尿多便溏者忌服", "quantity": 260, "unit": "g", "price": 45, "min_stock": 30},
    {"name": "络石藤", "alias": "络石", "category": "祛风湿药", "nature": "微寒", "taste": "苦", "meridian": "归心、肝、肾经", "efficacy": "祛风通络，凉血消肿", "indications": "风湿热痹，筋脉拘挛，腰膝酸痛，喉痹，痈肿，跌扑损伤", "usage": "煎服", "dosage": "6-12g", "contraindication": "阳虚畏寒，便溏者慎服", "quantity": 200, "unit": "g", "price": 25, "min_stock": 24},
    {"name": "穿山龙", "alias": "穿龙骨", "category": "祛风湿药", "nature": "平", "taste": "甘、苦", "meridian": "归肝、肾、肺经", "efficacy": "祛风除湿，舒筋通络，活血止痛，止咳平喘", "indications": "风湿痹病，关节肿胀，疼痛麻木，跌扑损伤，闪腰岔气，咳嗽气喘", "usage": "煎服", "dosage": "9-15g", "contraindication": "粉碎时注意防护，孕妇慎用", "quantity": 280, "unit": "g", "price": 28, "min_stock": 32},
    {"name": "五加皮", "alias": "南五加皮", "category": "祛风湿药", "nature": "温", "taste": "辛、苦", "meridian": "归肝、肾经", "efficacy": "祛风除湿，补益肝肾，强筋壮骨，利水消肿", "indications": "风湿痹病，筋骨痿软，小儿行迟，体虚乏力，水肿，脚气", "usage": "煎服", "dosage": "5-10g", "contraindication": "阴虚火旺者慎服", "quantity": 250, "unit": "g", "price": 32, "min_stock": 28},
    {"name": "桑寄生", "alias": "寄生", "category": "祛风湿药", "nature": "平", "taste": "苦、甘", "meridian": "归肝、肾经", "efficacy": "祛风湿，补肝肾，强筋骨，安胎元", "indications": "风湿痹痛，腰膝酸软，筋骨无力，崩漏经多，妊娠漏血，胎动不安，头晕目眩", "usage": "煎服", "dosage": "9-15g", "contraindication": "无特殊禁忌", "quantity": 280, "unit": "g", "price": 35, "min_stock": 32},
    {"name": "狗脊", "alias": "金毛狗脊", "category": "祛风湿药", "nature": "温", "taste": "苦、甘", "meridian": "归肝、肾经", "efficacy": "祛风湿，补肝肾，强腰膝", "indications": "风湿痹痛，腰膝酸软，下肢无力，尿频，遗尿，白带过多", "usage": "煎服", "dosage": "6-12g", "contraindication": "肾虚有热，小便不利或短涩黄赤者慎服", "quantity": 260, "unit": "g", "price": 38, "min_stock": 30},
    {"name": "千年健", "alias": "千年见", "category": "祛风湿药", "nature": "温", "taste": "苦、辛", "meridian": "归肝、肾经", "efficacy": "祛风湿，壮筋骨", "indications": "风寒湿痹，腰膝冷痛，下肢拘挛麻木", "usage": "煎服", "dosage": "5-10g", "contraindication": "阴虚内热者慎服", "quantity": 200, "unit": "g", "price": 42, "min_stock": 24},
    {"name": "雪莲花", "alias": "雪莲", "category": "祛风湿药", "nature": "温", "taste": "甘、微苦", "meridian": "归肝、肾经", "efficacy": "温肾壮阳，调经止血", "indications": "阳痿，腰膝酸软，女子崩漏，月经不调，风湿痹证，外伤出血", "usage": "煎服", "dosage": "6-12g", "contraindication": "孕妇忌服", "quantity": 50, "unit": "g", "price": 180, "min_stock": 10},
    {"name": "苍术", "alias": "赤术", "category": "化湿药", "nature": "温", "taste": "辛、苦", "meridian": "归脾、胃经", "efficacy": "燥湿健脾，祛风散寒，明目", "indications": "湿阻中焦，脘腹胀满，泄泻，水肿，脚气痿躄，风湿痹痛，风寒感冒，夜盲，眼目昏涩", "usage": "煎服", "dosage": "3-9g", "contraindication": "阴虚内热，气虚多汗者忌服", "quantity": 350, "unit": "g", "price": 25, "min_stock": 40},
    {"name": "厚朴", "alias": "川朴", "category": "化湿药", "nature": "温", "taste": "苦、辛", "meridian": "归脾、胃、肺、大肠经", "efficacy": "燥湿消痰，下气除满", "indications": "湿滞伤中，脘痞吐泻，食积气滞，腹胀便秘，痰饮喘咳", "usage": "煎服", "dosage": "3-10g", "contraindication": "孕妇慎用", "quantity": 280, "unit": "g", "price": 35, "min_stock": 32},
    {"name": "藿香", "alias": "广藿香", "category": "化湿药", "nature": "微温", "taste": "辛", "meridian": "归脾、胃、肺经", "efficacy": "芳香化浊，和中止呕，发表解暑", "indications": "湿浊中阻，脘痞呕吐，暑湿表证，湿温初起，发热倦怠，胸闷不舒，寒湿闭暑，腹痛吐泻，鼻渊头痛", "usage": "煎服", "dosage": "3-10g", "contraindication": "阴虚血燥者不宜用", "quantity": 320, "unit": "g", "price": 22, "min_stock": 38},
    {"name": "佩兰", "alias": "兰草", "category": "化湿药", "nature": "平", "taste": "辛", "meridian": "归脾、胃、肺经", "efficacy": "芳香化湿，醒脾开胃，发表解暑", "indications": "湿浊中阻，脘痞呕恶，口中甜腻，口臭，多涎，暑湿表证，湿温初起，发热倦怠，胸闷不舒", "usage": "煎服", "dosage": "3-10g", "contraindication": "阴虚血燥，气虚者慎服", "quantity": 280, "unit": "g", "price": 18, "min_stock": 32},
    {"name": "砂仁", "alias": "阳春砂", "category": "化湿药", "nature": "温", "taste": "辛", "meridian": "归脾、胃、肾经", "efficacy": "化湿开胃，温脾止泻，理气安胎", "indications": "湿浊中阻，脘痞不饥，脾胃虚寒，呕吐泄泻，妊娠恶阻，胎动不安", "usage": "后下", "dosage": "3-6g", "contraindication": "阴虚血燥者慎用", "quantity": 180, "unit": "g", "price": 85, "min_stock": 22},
    {"name": "豆蔻", "alias": "白豆蔻", "category": "化湿药", "nature": "温", "taste": "辛", "meridian": "归肺、脾、胃经", "efficacy": "化湿行气，温中止呕，开胃消食", "indications": "湿浊中阻，不思饮食，湿温初起，胸闷不饥，寒湿呕逆，胸腹胀痛，食积不消", "usage": "后下", "dosage": "3-6g", "contraindication": "阴虚血燥者慎用", "quantity": 150, "unit": "g", "price": 75, "min_stock": 18},
    {"name": "草豆蔻", "alias": "草蔻", "category": "化湿药", "nature": "温", "taste": "辛", "meridian": "归脾、胃经", "efficacy": "燥湿行气，温中止呕", "indications": "寒湿内阻，脘腹胀满冷痛，嗳气呕逆，不思饮食", "usage": "煎服", "dosage": "3-6g", "contraindication": "阴虚血燥者慎用", "quantity": 180, "unit": "g", "price": 45, "min_stock": 22},
    {"name": "草果", "alias": "草果仁", "category": "化湿药", "nature": "温", "taste": "辛", "meridian": "归脾、胃经", "efficacy": "燥湿温中，除痰截疟", "indications": "寒湿内阻，脘腹胀痛，痞满呕吐，疟疾寒热，瘟疫发热", "usage": "煎服", "dosage": "3-6g", "contraindication": "阴虚血燥者慎用", "quantity": 200, "unit": "g", "price": 38, "min_stock": 24},
]

def add_new_medicines():
    print("=" * 60)
    print("添加更多药材到300味")
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
    print("最终统计")
    print("=" * 60)
    
    med_count = db.fetchone("SELECT COUNT(*) FROM medicines")[0]
    inv_count = db.fetchone("SELECT COUNT(*) FROM inventory")[0]
    
    print(f"\n新增药材: {added} 味")
    print(f"错误: {errors}")
    print(f"\n当前药材总数: {med_count}")
    print(f"当前库存记录: {inv_count}")
    
    db.close()

if __name__ == '__main__':
    add_new_medicines()
    input("\n按任意键退出...")