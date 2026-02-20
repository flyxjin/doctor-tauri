import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

final_medicines = [
    {"name": "泽泻", "alias": "水泻", "category": "利水渗湿药", "nature": "寒", "taste": "甘、淡", "meridian": "归肾、膀胱经", "efficacy": "利水渗湿，泄热，化浊降脂", "indications": "小便不利，水肿胀满，泄泻尿少，痰饮眩晕，热淋涩痛，高脂血症", "usage": "煎服", "dosage": "6-10g", "contraindication": "肾虚滑精者慎服", "quantity": 350, "unit": "g", "price": 22, "min_stock": 40},
    {"name": "薏苡仁", "alias": "薏米", "category": "利水渗湿药", "nature": "凉", "taste": "甘、淡", "meridian": "归脾、胃、肺经", "efficacy": "利水渗湿，健脾止泻，除痹，排脓，解毒散结", "indications": "水肿，脚气，小便不利，脾虚泄泻，湿痹拘挛，肺痈，肠痈，赘疣，癌肿", "usage": "煎服", "dosage": "9-30g", "contraindication": "孕妇慎用", "quantity": 400, "unit": "g", "price": 18, "min_stock": 45},
    {"name": "车前子", "alias": "车前实", "category": "利水渗湿药", "nature": "寒", "taste": "甘", "meridian": "归肝、肾、肺、小肠经", "efficacy": "清热利尿通淋，渗湿止泻，明目，祛痰", "indications": "热淋涩痛，水肿胀满，暑湿泄泻，目赤肿痛，痰热咳嗽", "usage": "包煎", "dosage": "9-15g", "contraindication": "肾虚精滑者慎用", "quantity": 280, "unit": "g", "price": 25, "min_stock": 32},
    {"name": "滑石", "alias": "画石", "category": "利水渗湿药", "nature": "寒", "taste": "甘、淡", "meridian": "归膀胱、肺、胃经", "efficacy": "利尿通淋，清热解暑，外用祛湿敛疮", "indications": "热淋，石淋，尿热涩痛，暑湿烦渴，湿热水泻，外治湿疹，湿疮，痱子", "usage": "包煎", "dosage": "10-20g", "contraindication": "脾虚气弱，精滑及热病津伤者忌服，孕妇慎用", "quantity": 300, "unit": "g", "price": 12, "min_stock": 35},
    {"name": "木通", "alias": "通草", "category": "利水渗湿药", "nature": "寒", "taste": "苦", "meridian": "归心、小肠、膀胱经", "efficacy": "利尿通淋，清心除烦，通经下乳", "indications": "淋证，水肿，心烦尿赤，口舌生疮，经闭乳少，湿热痹痛", "usage": "煎服", "dosage": "3-6g", "contraindication": "孕妇慎用，内无湿热，津亏，精滑，小便频数者忌服", "quantity": 200, "unit": "g", "price": 35, "min_stock": 24},
    {"name": "通草", "alias": "大通草", "category": "利水渗湿药", "nature": "微寒", "taste": "甘、淡", "meridian": "归肺、胃经", "efficacy": "清热利尿，通气下乳", "indications": "湿热尿赤，淋证涩痛，水肿尿少，乳汁不下", "usage": "煎服", "dosage": "3-5g", "contraindication": "孕妇慎用", "quantity": 180, "unit": "g", "price": 28, "min_stock": 22},
    {"name": "瞿麦", "alias": "巨麦", "category": "利水渗湿药", "nature": "寒", "taste": "苦", "meridian": "归心、小肠经", "efficacy": "利尿通淋，破血通经", "indications": "热淋，血淋，石淋，小便不通，淋沥涩痛，经闭瘀阻", "usage": "煎服", "dosage": "9-15g", "contraindication": "孕妇慎用", "quantity": 220, "unit": "g", "price": 18, "min_stock": 26},
    {"name": "萹蓄", "alias": "扁蓄", "category": "利水渗湿药", "nature": "微寒", "taste": "苦", "meridian": "归膀胱经", "efficacy": "利尿通淋，杀虫，止痒", "indications": "热淋，血淋，石淋，小便涩痛，皮肤湿疹，阴痒带下", "usage": "煎服", "dosage": "9-15g", "contraindication": "脾虚者慎用", "quantity": 200, "unit": "g", "price": 15, "min_stock": 24},
    {"name": "地肤子", "alias": "扫帚子", "category": "利水渗湿药", "nature": "寒", "taste": "辛、苦", "meridian": "归肾、膀胱经", "efficacy": "清热利湿，祛风止痒", "indications": "小便涩痛，阴痒带下，风疹，湿疹，皮肤瘙痒", "usage": "煎服", "dosage": "9-15g", "contraindication": "内无湿热，尿多者慎服", "quantity": 250, "unit": "g", "price": 18, "min_stock": 30},
    {"name": "海金沙", "alias": "金沙藤", "category": "利水渗湿药", "nature": "寒", "taste": "甘、咸", "meridian": "归膀胱、小肠经", "efficacy": "清利湿热，通淋止痛", "indications": "热淋，石淋，血淋，膏淋，尿道涩痛", "usage": "包煎", "dosage": "6-15g", "contraindication": "肾阴亏虚者慎服", "quantity": 180, "unit": "g", "price": 45, "min_stock": 22},
    {"name": "石韦", "alias": "石皮", "category": "利水渗湿药", "nature": "微寒", "taste": "甘、苦", "meridian": "归肺、膀胱经", "efficacy": "利尿通淋，清肺止咳，凉血止血", "indications": "热淋，血淋，石淋，小便不通，淋沥涩痛，肺热喘咳，吐血，衄血，尿血，崩漏", "usage": "煎服", "dosage": "6-12g", "contraindication": "阴虚及无湿热者忌服", "quantity": 200, "unit": "g", "price": 32, "min_stock": 24},
    {"name": "冬葵子", "alias": "葵子", "category": "利水渗湿药", "nature": "寒", "taste": "甘", "meridian": "归大肠、小肠、膀胱经", "efficacy": "利尿通淋，下乳，润肠", "indications": "淋证，水肿，乳汁不通，乳房胀痛，肠燥便秘", "usage": "煎服", "dosage": "3-9g", "contraindication": "孕妇慎用，脾虚便溏者忌服", "quantity": 180, "unit": "g", "price": 28, "min_stock": 22},
    {"name": "灯心草", "alias": "灯草", "category": "利水渗湿药", "nature": "微寒", "taste": "甘、淡", "meridian": "归心、肺、小肠经", "efficacy": "清心火，利小便", "indications": "心烦失眠，尿少涩痛，口舌生疮", "usage": "煎服", "dosage": "1-3g", "contraindication": "虚寒者慎服", "quantity": 150, "unit": "g", "price": 22, "min_stock": 18},
    {"name": "萆薢", "alias": "粉萆薢", "category": "利水渗湿药", "nature": "平", "taste": "苦", "meridian": "归肾、胃经", "efficacy": "利湿去浊，祛风除痹", "indications": "膏淋，白浊，白带过多，风湿痹痛，关节不利，腰膝疼痛", "usage": "煎服", "dosage": "9-15g", "contraindication": "肾阴亏虚者慎服", "quantity": 220, "unit": "g", "price": 28, "min_stock": 26},
    {"name": "茵陈", "alias": "茵陈蒿", "category": "利水渗湿药", "nature": "微寒", "taste": "苦、辛", "meridian": "归脾、胃、肝、胆经", "efficacy": "清利湿热，利胆退黄", "indications": "黄疸尿少，湿温暑湿，湿疮瘙痒", "usage": "煎服", "dosage": "6-15g", "contraindication": "蓄血发黄者忌服，血虚萎黄者慎用", "quantity": 300, "unit": "g", "price": 18, "min_stock": 35},
]

def add_final_medicines():
    print("=" * 60)
    print("添加最后15味药材到300味")
    print("=" * 60)
    
    db = Database()
    
    added = 0
    errors = 0
    
    for medicine in final_medicines:
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
    
    categories = db.fetchall("SELECT category, COUNT(*) FROM medicines WHERE category IS NOT NULL AND category != '' GROUP BY category")
    
    print(f"\n新增药材: {added} 味")
    print(f"错误: {errors}")
    print(f"\n当前药材总数: {med_count}")
    print(f"当前库存记录: {inv_count}")
    
    print("\n药材分类统计:")
    for cat, count in categories:
        print(f"  {cat}: {count} 味")
    
    db.close()

if __name__ == '__main__':
    add_final_medicines()
    input("\n按任意键退出...")