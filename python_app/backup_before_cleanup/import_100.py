
import sys
import os
import csv
import sqlite3
from datetime import datetime

def main():
    print("=" * 60)
    print("   Import 100 Chinese Medicines")
    print("=" * 60)
    
    csv_file = "大药房库存录入模板_100味.csv"
    db_file = "medicine_system.db"
    
    if not os.path.exists(csv_file):
        print("ERROR: File not found: " + csv_file)
        return
    
    print("\nData file found")
    print("Connecting to database...")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("Database connected")
    print("\nStarting import...\n")
    
    success_count = 0
    failed_count = 0
    errors = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data_list = list(reader)
        
        total = len(data_list)
        print("Total records: " + str(total) + "\n")
        
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
                print("[" + str(row_num) + "/" + str(total) + "] OK: " + name)
                
            except Exception as e:
                failed_count += 1
                errors.append({"row": row_num, "name": name, "error": str(e)})
                print("[" + str(row_num) + "/" + str(total) + "] FAIL: " + name + " - " + str(e))
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("Import Complete!")
        print("Total: " + str(total) + ", Success: " + str(success_count) + ", Failed: " + str(failed_count))
        
        if success_count == 100:
            print("\nSUCCESS: All 100 medicines imported!")
        
        report_file = "import_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(generate_report(total, success_count, failed_count, errors))
        print("\nReport saved to: " + report_file)
        
    except Exception as e:
        conn.rollback()
        print("Import failed: " + str(e))
    finally:
        conn.close()

def generate_report(total, success, failed, errors):
    report = []
    report.append("=" * 60)
    report.append("          Import Report")
    report.append("=" * 60)
    report.append("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report.append("")
    report.append("-" * 60)
    report.append("Statistics")
    report.append("-" * 60)
    report.append("Total: " + str(total))
    report.append("Success: " + str(success))
    report.append("Failed: " + str(failed))
    
    if errors:
        report.append("")
        report.append("-" * 60)
        report.append("Errors")
        report.append("-" * 60)
        for err in errors[:20]:
            report.append("Row " + str(err.get("row", "?")) + ": " + err.get("name", "Unknown") + " - " + err.get("error", ""))
        if len(errors) &gt; 20:
            report.append("... and " + str(len(errors) - 20) + " more errors")
    
    report.append("")
    report.append("=" * 60)
    report.append("End of Report")
    report.append("=" * 60)
    
    return "\n".join(report)

if __name__ == '__main__':
    main()

