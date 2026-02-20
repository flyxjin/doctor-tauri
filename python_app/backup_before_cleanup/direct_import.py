
import sys
import os
import csv
import sqlite3
from datetime import datetime

def main():
    print("=" * 60)
    print("   大药房100味中药材直接导入工具")
    print("=" * 60)
    
    csv_file = "大药房库存录入模板_100味.csv"
    db_file = "medicine_system.db"
    
    if not os.path.exists(csv_file):
        print("错误：找不到数据文件 " + csv_file)
        return
    
    print("\n找到数据文件")
    print("正在连接数据库...")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("数据库连接成功")
    print("\n开始导入...\n")
    
    success_count = 0
    failed_count = 0
    errors = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data_list = list(reader)
        
        total = len(data_list)
        print("共 " + str(total) + " 条记录待导入\n")
        
        for idx, row in enumerate(data_list):
            row_num = idx + 1
            name = row.get('name', '')
            
            try:
                cursor.execute("SELECT id FROM medicines WHERE name = ?", (name,))
                existing = cursor.fetchone()
                
                if existing:
                    med_id = existing[0]
                    cursor.execute('''
                        UPDATE medicines 
                        SET alias=?, category=?, nature=?, taste=?, meridian=?, 
                            efficacy=?, indications=?, usage=?, dosage=?, 
                            contraindication=?, notes=?, origin=?, grade=?
                        WHERE id=?
                    ''', (
                        row.get('alias', ''),
                        row.get('category', ''),
                        row.get('nature', ''),
                        row.get('taste', ''),
                        row.get('meridian', ''),
                        row.get('efficacy', ''),
                        row.get('indications', ''),
                        row.get('usage', ''),
                        row.get('dosage', ''),
                        row.get('contraindication', ''),
                        row.get('notes', ''),
                        row.get('origin', ''),
                        row.get('grade', ''),
                        med_id
                    ))
                    
                    cursor.execute("SELECT id, quantity FROM inventory WHERE medicine_id = ?", (med_id,))
                    inv_existing = cursor.fetchone()
                    
                    if inv_existing:
                        inv_id, current_qty = inv_existing
                        new_qty = float(current_qty) + float(row.get('quantity', 0))
                        cursor.execute('''
                            UPDATE inventory 
                            SET quantity=?, price=?, min_stock=?, 
                                purchase_date=?, expiry_date=?, supplier=?,
                                batch_number=?, storage_location=?, quality_status=?
                            WHERE id=?
                        ''', (
                            new_qty,
                            float(row.get('price', 0)),
                            float(row.get('min_stock', 10)),
                            row.get('purchase_date', ''),
                            row.get('expiry_date', ''),
                            row.get('supplier', ''),
                            row.get('batch_number', ''),
                            row.get('storage_location', ''),
                            row.get('quality_status', '合格'),
                            inv_id
                        ))
                    else:
                        cursor.execute('''
                            INSERT INTO inventory (
                                medicine_id, quantity, unit, price, min_stock,
                                purchase_date, expiry_date, supplier, batch_number,
                                storage_location, quality_status
                            ) VALUES (?, ?, 'g', ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            med_id,
                            float(row.get('quantity', 0)),
                            float(row.get('price', 0)),
                            float(row.get('min_stock', 10)),
                            row.get('purchase_date', ''),
                            row.get('expiry_date', ''),
                            row.get('supplier', ''),
                            row.get('batch_number', ''),
                            row.get('storage_location', ''),
                            row.get('quality_status', '合格')
                        ))
                else:
                    cursor.execute('''
                        INSERT INTO medicines (
                            name, alias, category, nature, taste, meridian,
                            efficacy, indications, usage, dosage, contraindication,
                            notes, origin, grade
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        name,
                        row.get('alias', ''),
                        row.get('category', ''),
                        row.get('nature', ''),
                        row.get('taste', ''),
                        row.get('meridian', ''),
                        row.get('efficacy', ''),
                        row.get('indications', ''),
                        row.get('usage', ''),
                        row.get('dosage', ''),
                        row.get('contraindication', ''),
                        row.get('notes', ''),
                        row.get('origin', ''),
                        row.get('grade', '')
                    ))
                    
                    med_id = cursor.lastrowid
                    
                    cursor.execute('''
                        INSERT INTO inventory (
                            medicine_id, quantity, unit, price, min_stock,
                            purchase_date, expiry_date, supplier, batch_number,
                            storage_location, quality_status
                        ) VALUES (?, ?, 'g', ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        med_id,
                        float(row.get('quantity', 0)),
                        float(row.get('price', 0)),
                        float(row.get('min_stock', 10)),
                        row.get('purchase_date', ''),
                        row.get('expiry_date', ''),
                        row.get('supplier', ''),
                        row.get('batch_number', ''),
                        row.get('storage_location', ''),
                        row.get('quality_status', '合格')
                    ))
                
                success_count += 1
                print("[" + str(row_num) + "/" + str(total) + "] 成功: " + name)
                
            except Exception as e:
                failed_count += 1
                errors.append({"row": row_num, "name": name, "error": str(e)})
                print("[" + str(row_num) + "/" + str(total) + "] 失败: " + name + " - " + str(e))
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("导入完成！")
        print("总计: " + str(total) + ", 成功: " + str(success_count) + ", 失败: " + str(failed_count))
        
        if success_count == 100:
            print("\n恭喜！100味药材全部导入成功！")
        
        report = generate_report(total, success_count, failed_count, errors)
        with open("导入报告.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        print("\n详细报告已保存至: 导入报告.txt")
        
    except Exception as e:
        conn.rollback()
        print("导入失败: " + str(e))
    finally:
        conn.close()

def generate_report(total, success, failed, errors):
    report = []
    report.append("=" * 60)
    report.append("          大药房中草药库存录入报告")
    report.append("=" * 60)
    report.append("报告生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report.append("")
    report.append("-" * 60)
    report.append("录入统计")
    report.append("-" * 60)
    report.append("总记录数: " + str(total))
    report.append("成功录入: " + str(success))
    report.append("失败记录: " + str(failed))
    
    if errors:
        report.append("")
        report.append("-" * 60)
        report.append("错误详情")
        report.append("-" * 60)
        for err in errors[:20]:
            report.append("行" + str(err.get("row", "?")) + ": " + err.get("name", "未知") + " - " + err.get("error", ""))
        if len(errors) &gt; 20:
            report.append("... 还有 " + str(len(errors) - 20) + " 条错误")
    
    report.append("")
    report.append("=" * 60)
    report.append("报告结束")
    report.append("=" * 60)
    
    return "\n".join(report)

if __name__ == '__main__':
    main()

