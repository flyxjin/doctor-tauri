
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from 药材数据 import medicines_list

print("=" * 60)
print("   300味中药材导入工具")
print("=" * 60)

db = Database()

print("\n开始导入药材数据...\n")

success_count = 0
update_count = 0
skip_count = 0

for idx, med in enumerate(medicines_list):
    name = med.get("name", "")
    print(f"[{idx+1}/{len(medicines_list)}] 处理: {name}", end="")
    
    try:
        existing = db.fetchone("SELECT id FROM medicines WHERE name = ?", (name,))
        
        if existing:
            med_id = existing[0]
            db.execute('''
                UPDATE medicines 
                SET alias=?, category=?, nature=?, taste=?, meridian=?, 
                    efficacy=?, indications=?, usage=?, dosage=?, 
                    contraindication=?, notes=?
                WHERE id=?
            ''', (
                med.get("alias", ""),
                med.get("category", ""),
                med.get("nature", ""),
                med.get("taste", ""),
                med.get("meridian", ""),
                med.get("efficacy", ""),
                med.get("indications", ""),
                med.get("usage", ""),
                med.get("dosage", ""),
                med.get("contraindication", ""),
                med.get("notes", ""),
                med_id
            ))
            
            inv_existing = db.fetchone("SELECT id FROM inventory WHERE medicine_id = ?", (med_id,))
            if inv_existing:
                db.execute('''
                    UPDATE inventory 
                    SET quantity=?, unit=?, price=?, min_stock=?, notes=?
                    WHERE medicine_id=?
                ''', (
                    med.get("quantity", 0),
                    med.get("unit", "g"),
                    med.get("price", 0),
                    med.get("min_stock", 10),
                    med.get("notes", ""),
                    med_id
                ))
            else:
                db.execute('''
                    INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    med_id,
                    med.get("quantity", 0),
                    med.get("unit", "g"),
                    med.get("price", 0),
                    med.get("min_stock", 10),
                    med.get("notes", "")
                ))
            
            update_count += 1
            print(" - 更新")
        else:
            db.execute('''
                INSERT INTO medicines (
                    name, alias, category, nature, taste, meridian,
                    efficacy, indications, usage, dosage, contraindication, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                med.get("alias", ""),
                med.get("category", ""),
                med.get("nature", ""),
                med.get("taste", ""),
                med.get("meridian", ""),
                med.get("efficacy", ""),
                med.get("indications", ""),
                med.get("usage", ""),
                med.get("dosage", ""),
                med.get("contraindication", ""),
                med.get("notes", "")
            ))
            
            med_id = db.cursor.lastrowid
            
            db.execute('''
                INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                med_id,
                med.get("quantity", 0),
                med.get("unit", "g"),
                med.get("price", 0),
                med.get("min_stock", 10),
                med.get("notes", "")
            ))
            
            success_count += 1
            print(" - 新增")
            
    except Exception as e:
        skip_count += 1
        print(f" - 跳过: {str(e)}")

db.commit()
db.close()

print("\n" + "=" * 60)
print("导入完成！")
print("=" * 60)
print(f"新增药材: {success_count} 味")
print(f"更新药材: {update_count} 味")
print(f"跳过药材: {skip_count} 味")
print(f"总计处理: {len(medicines_list)} 味")
print("=" * 60)

