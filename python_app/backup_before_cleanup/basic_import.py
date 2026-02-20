
import sys
import os
import csv
import sqlite3
from datetime import datetime

csv_file = "大药房库存录入模板_100味.csv"
db_file = "medicine_system.db"

print("=" * 60)
print("   Import Tool")
print("=" * 60)

if not os.path.exists(csv_file):
    print("ERROR: File not found")
    sys.exit(1)

print("\nFile found")
print("Connecting to database...")

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print("Database connected")
print("\nReading CSV...")

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    data_list = list(reader)

total = len(data_list)
print("Total: " + str(total))
print("\nStarting import...\n")

success = 0
failed = 0

for idx, row in enumerate(data_list):
    row_num = idx + 1
    name = row.get('name', '')
    
    try:
        cursor.execute("SELECT id FROM medicines WHERE name = ?", (name,))
        existing = cursor.fetchone()
        
        if existing:
            med_id = existing[0]
            cursor.execute('''
                UPDATE medicines SET alias=?, category=?, nature=?, taste=?, 
                meridian=?, efficacy=?, indications=?, usage=?, dosage=?, 
                contraindication=?, notes=?, origin=?, grade=? WHERE id=?
            ''', (
                row.get('alias', ''), row.get('category', ''), 
                row.get('nature', ''), row.get('taste', ''), 
                row.get('meridian', ''), row.get('efficacy', ''), 
                row.get('indications', ''), row.get('usage', ''), 
                row.get('dosage', ''), row.get('contraindication', ''), 
                row.get('notes', ''), row.get('origin', ''), 
                row.get('grade', ''), med_id
            ))
            
            cursor.execute("SELECT id, quantity FROM inventory WHERE medicine_id = ?", (med_id,))
            inv_existing = cursor.fetchone()
            
            if inv_existing:
                inv_id, current_qty = inv_existing
                new_qty = float(current_qty) + float(row.get('quantity', 0))
                cursor.execute('''
                    UPDATE inventory SET quantity=?, price=?, min_stock=?, 
                    purchase_date=?, expiry_date=?, supplier=?, 
                    batch_number=?, storage_location=?, quality_status=? WHERE id=?
                ''', (
                    new_qty, float(row.get('price', 0)), 
                    float(row.get('min_stock', 10)), 
                    row.get('purchase_date', ''), 
                    row.get('expiry_date', ''), 
                    row.get('supplier', ''), 
                    row.get('batch_number', ''), 
                    row.get('storage_location', ''), 
                    row.get('quality_status', '合格'), inv_id
                ))
            else:
                cursor.execute('''
                    INSERT INTO inventory (medicine_id, quantity, unit, price, 
                    min_stock, purchase_date, expiry_date, supplier, 
                    batch_number, storage_location, quality_status)
                    VALUES (?, ?, 'g', ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    med_id, float(row.get('quantity', 0)), 
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
                INSERT INTO medicines (name, alias, category, nature, taste, 
                meridian, efficacy, indications, usage, dosage, 
                contraindication, notes, origin, grade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, row.get('alias', ''), row.get('category', ''), 
                row.get('nature', ''), row.get('taste', ''), 
                row.get('meridian', ''), row.get('efficacy', ''), 
                row.get('indications', ''), row.get('usage', ''), 
                row.get('dosage', ''), row.get('contraindication', ''), 
                row.get('notes', ''), row.get('origin', ''), 
                row.get('grade', '')
            ))
            
            med_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO inventory (medicine_id, quantity, unit, price, 
                min_stock, purchase_date, expiry_date, supplier, 
                batch_number, storage_location, quality_status)
                VALUES (?, ?, 'g', ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                med_id, float(row.get('quantity', 0)), 
                float(row.get('price', 0)), 
                float(row.get('min_stock', 10)), 
                row.get('purchase_date', ''), 
                row.get('expiry_date', ''), 
                row.get('supplier', ''), 
                row.get('batch_number', ''), 
                row.get('storage_location', ''), 
                row.get('quality_status', '合格')
            ))
        
        success += 1
        print("[" + str(row_num) + "/" + str(total) + "] OK: " + name)
        
    except Exception as e:
        failed += 1
        print("[" + str(row_num) + "/" + str(total) + "] FAIL: " + name)

conn.commit()

print("\n" + "=" * 60)
print("Import Complete!")
print("Total: " + str(total) + ", Success: " + str(success) + ", Failed: " + str(failed))

if success == 100:
    print("\nSUCCESS: All 100 medicines imported!")

conn.close()

print("\nDone!")

