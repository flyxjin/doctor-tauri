import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from medicines_data_300 import medicines_300

def import_300_medicines():
    print("=" * 60)
    print("开始导入300味中药材数据")
    print("=" * 60)
    
    db = Database()
    
    total = len(medicines_300)
    added = 0
    updated = 0
    skipped = 0
    errors = 0
    
    print(f"\n准备导入 {total} 味药材...\n")
    
    try:
        db.begin_transaction()
        
        for i, medicine in enumerate(medicines_300, 1):
            try:
                name = medicine['name']
                print(f"[{i}/{total}] 处理: {name}", end=" - ")
                
                existing = db.fetchone(
                    "SELECT id FROM medicines WHERE name = ?", 
                    (name,)
                )
                
                if existing:
                    db.execute('''
                        UPDATE medicines 
                        SET alias=?, category=?, nature=?, taste=?, meridian=?,
                            efficacy=?, indications=?, usage=?, dosage=?, 
                            contraindication=?, notes=?
                        WHERE id=?
                    ''', (
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
                        medicine.get('notes', ''),
                        existing[0]
                    ))
                    
                    db.execute('''
                        UPDATE inventory 
                        SET quantity=?, unit=?, price=?, min_stock=?, notes=?
                        WHERE medicine_id=?
                    ''', (
                        medicine.get('quantity', 0),
                        medicine.get('unit', 'g'),
                        medicine.get('price', 0),
                        medicine.get('min_stock', 10),
                        medicine.get('notes', ''),
                        existing[0]
                    ))
                    updated += 1
                    print("更新成功")
                else:
                    db.execute('''
                        INSERT INTO medicines 
                        (name, alias, category, nature, taste, meridian, 
                         efficacy, indications, usage, dosage, contraindication, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        name,
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
                        (name,)
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
                    print("新增成功")
                    
            except Exception as e:
                errors += 1
                print(f"错误: {str(e)}")
                continue
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("导入完成！")
        print("=" * 60)
        print(f"总计: {total} 味药材")
        print(f"新增: {added} 味")
        print(f"更新: {updated} 味")
        print(f"错误: {errors} 味")
        print("=" * 60)
        
        return True, added, updated, errors
        
    except Exception as e:
        db.rollback()
        print(f"\n导入失败: {str(e)}")
        return False, 0, 0, errors
    finally:
        db.close()

def verify_data():
    print("\n" + "=" * 60)
    print("数据验证")
    print("=" * 60)
    
    db = Database()
    
    try:
        med_count = db.fetchone("SELECT COUNT(*) FROM medicines")[0]
        inv_count = db.fetchone("SELECT COUNT(*) FROM inventory")[0]
        
        print(f"\n药材表记录数: {med_count}")
        print(f"库存表记录数: {inv_count}")
        
        categories = db.fetchall("SELECT category, COUNT(*) FROM medicines WHERE category IS NOT NULL AND category != '' GROUP BY category")
        print(f"\n药材分类统计:")
        for cat, count in categories:
            print(f"  {cat}: {count} 味")
        
        natures = db.fetchall("SELECT nature, COUNT(*) FROM medicines WHERE nature IS NOT NULL AND nature != '' GROUP BY nature")
        print(f"\n药性统计:")
        for nat, count in natures:
            print(f"  {nat}: {count} 味")
        
        low_stock = db.fetchall('''
            SELECT m.name, i.quantity, i.min_stock 
            FROM inventory i 
            JOIN medicines m ON i.medicine_id = m.id 
            WHERE i.quantity < i.min_stock
        ''')
        print(f"\n低库存药材: {len(low_stock)} 味")
        
        print("\n" + "=" * 60)
        print("验证完成！")
        print("=" * 60)
        
        return med_count, inv_count
        
    finally:
        db.close()

if __name__ == '__main__':
    success, added, updated, errors = import_300_medicines()
    
    if success:
        verify_data()
    
    print("\n按任意键退出...")
    input()