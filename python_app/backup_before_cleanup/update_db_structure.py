import sqlite3
import shutil
from datetime import datetime

def migrate_database():
    db_path = 'medicine_system.db'
    backup_path = f'medicine_system_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print("=" * 60)
    print("数据库迁移")
    print("=" * 60)
    
    print(f"\n1. 创建数据库备份: {backup_path}")
    shutil.copy2(db_path, backup_path)
    print("   备份完成！")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n2. 检查并更新medicines表结构")
    
    cursor.execute("PRAGMA table_info(medicines)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"   当前列: {columns}")
    
    if 'notes' not in columns:
        print("   添加notes列...")
        cursor.execute("ALTER TABLE medicines ADD COLUMN notes TEXT")
        print("   完成！")
    
    if 'alias' not in columns:
        print("   添加alias列...")
        cursor.execute("ALTER TABLE medicines ADD COLUMN alias TEXT")
        print("   完成！")
    
    if 'category' not in columns:
        print("   添加category列...")
        cursor.execute("ALTER TABLE medicines ADD COLUMN category TEXT")
        print("   完成！")
    
    if 'indications' not in columns:
        print("   添加indications列...")
        cursor.execute("ALTER TABLE medicines ADD COLUMN indications TEXT")
        print("   完成！")
    
    print("\n3. 检查并更新inventory表结构")
    
    cursor.execute("PRAGMA table_info(inventory)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"   当前列: {columns}")
    
    if 'notes' not in columns:
        print("   添加notes列...")
        cursor.execute("ALTER TABLE inventory ADD COLUMN notes TEXT")
        print("   完成！")
    
    conn.commit()
    
    print("\n4. 验证更新后的结构")
    
    cursor.execute("PRAGMA table_info(medicines)")
    meds_columns = [col[1] for col in cursor.fetchall()]
    print(f"   medicines表列: {meds_columns}")
    
    cursor.execute("PRAGMA table_info(inventory)")
    inv_columns = [col[1] for col in cursor.fetchall()]
    print(f"   inventory表列: {inv_columns}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("数据库迁移完成！")
    print("=" * 60)
    print(f"\n备份文件: {backup_path}")
    print("\n现在可以运行导入脚本了。")

if __name__ == '__main__':
    migrate_database()
    input("\n按任意键退出...")