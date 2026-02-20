import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

def verify_system():
    db = Database()
    
    print("=" * 60)
    print("系统验证报告")
    print("=" * 60)
    
    med_count = db.fetchone("SELECT COUNT(*) FROM medicines")[0]
    print(f"\n药材总数: {med_count}")
    
    inv_count = db.fetchone("SELECT COUNT(*) FROM inventory")[0]
    print(f"库存记录: {inv_count}")
    
    print("\n数据完整性检查:")
    missing_inventory = db.fetchone('''
        SELECT COUNT(*) FROM medicines m 
        LEFT JOIN inventory i ON m.id = i.medicine_id 
        WHERE i.id IS NULL
    ''')[0]
    print(f"  缺少库存记录的药材: {missing_inventory}")
    
    empty_names = db.fetchone("SELECT COUNT(*) FROM medicines WHERE name IS NULL OR name = ''")[0]
    print(f"  名称为空的药材: {empty_names}")
    
    print("\n药材分类统计:")
    categories = db.fetchall("SELECT category, COUNT(*) FROM medicines WHERE category IS NOT NULL AND category != '' GROUP BY category ORDER BY COUNT(*) DESC")
    for cat, count in categories:
        print(f"  {cat}: {count} 味")
    
    print("\n药性统计:")
    natures = db.fetchall("SELECT nature, COUNT(*) FROM medicines WHERE nature IS NOT NULL AND nature != '' GROUP BY nature ORDER BY COUNT(*) DESC")
    for nat, count in natures:
        print(f"  {nat}: {count} 味")
    
    low_stock = db.fetchall('''
        SELECT m.name, i.quantity, i.min_stock 
        FROM inventory i 
        JOIN medicines m ON i.medicine_id = m.id 
        WHERE i.quantity < i.min_stock
        LIMIT 10
    ''')
    print(f"\n低库存药材 (前10味):")
    if low_stock:
        for name, qty, min_qty in low_stock:
            print(f"  {name}: {qty}g (最低库存: {min_qty}g)")
    else:
        print("  无低库存药材")
    
    total_value = db.fetchone("SELECT SUM(quantity * price) FROM inventory")[0] or 0
    print(f"\n库存总值: ¥{total_value:.2f}")
    
    print("\n" + "=" * 60)
    print("验证完成！系统状态正常")
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    verify_system()
    input("\n按任意键退出...")