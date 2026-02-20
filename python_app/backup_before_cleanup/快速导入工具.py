
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from inventory_entry import InventoryEntrySystem


def import_100_medicines():
    print("=" * 70)
    print("          大药房100味中药材快速导入工具")
    print("=" * 70)
    
    csv_file = os.path.join(os.path.dirname(__file__), '大药房库存录入模板_100味.csv')
    
    if not os.path.exists(csv_file):
        print("错误: 找不到文件 大药房库存录入模板_100味.csv")
        print("请确保文件位于正确的位置！")
        input("\n按回车键退出...")
        return
    
    print("\n找到数据文件: 大药房库存录入模板_100味.csv")
    print("正在连接数据库...")
    
    try:
        db = Database()
        entry_system = InventoryEntrySystem(db)
        
        print("数据库连接成功")
        print("\n开始批量导入数据，请稍候...\n")
        
        results = entry_system.batch_import_from_csv(csv_file, '快速导入工具')
        
        report = entry_system.generate_entry_report(results)
        print(report)
        
        success_count = results.get('success', 0)
        if success_count == 100:
            print("\n恭喜！100味药材全部导入成功！")
        elif success_count &gt; 0:
            print("\n成功导入 " + str(success_count) + " 味药材")
        
        print("\n" + "=" * 70)
        
        report_file = os.path.join(os.path.dirname(__file__), '导入报告.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print("详细报告已保存至: 导入报告.txt")
        
        db.close()
        
    except Exception as e:
        print("\n导入过程中发生错误: " + str(e))
        import traceback
        traceback.print_exc()
    
    print("\n按回车键退出...")
    input()


if __name__ == '__main__':
    import_100_medicines()

