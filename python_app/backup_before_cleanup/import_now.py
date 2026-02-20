
import sys
import os
import sqlite3

csv_file = "大药房库存录入模板_100味.csv"
db_file = "medicine_system.db"

print("Import Tool")

if not os.path.exists(csv_file):
    print("ERROR: File not found")
    sys.exit(1)

print("File found")

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print("Database connected")

lines = []
with open(csv_file, 'r', encoding='utf-8-sig') as f:
    for line in f:
        lines.append(line.strip())

if len(lines) &lt; 2:
    print("ERROR: CSV file is empty")
    sys.exit(1)

headers = lines[0].split(',')
headers = [h.strip() for h in headers]

print("Processing data...")

success = 0
failed = 0

for i in range(1, len(lines)):
    line = lines[i]
    if not line:
        continue
    
    values = line.split(',')
    while len(values) &lt; len(headers):
        values.append('')
    
    row = {}
    for j in range(min(len(headers), len(values))):
        row[headers[j]] = values[j].strip()
    
    name = row.get('name', '')
    
    try:
        if not name:
            failed += 1
            continue
        
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
            
            qty_val = row.get('quantity', '0')
            price_val = row.get('price', '0')
            min_stock_val = row.get('min_stock', '10')
            
            if inv_existing:
                inv_id, current_qty = inv_existing
                new_qty = float(current_qty) + float(qty_val)
                
                cursor.execute('''
                    UPDATE inventory SET quantity=?, price=?, min_stock=?, 
                    purchase_date=?, expiry_date=?, supplier=?, 
                    batch_number=?, storage_location=?, quality_status=? WHERE id=?
                ''', (
                    new_qty, float(price_val) if price_val else 0, 
                    float(min_stock_val) if min_stock_val else 10, 
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
                    med_id, float(qty_val) if qty_val else 0, 
                    float(price_val) if price_val else 0, 
                    float(min_stock_val) if min_stock_val else 10, 
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
            
            qty_val = row.get('quantity', '0')
            price_val = row.get('price', '0')
            min_stock_val = row.get('min_stock', '10')
            
            cursor.execute('''
                INSERT INTO inventory (medicine_id, quantity, unit, price, 
                min_stock, purchase_date, expiry_date, supplier, 
                batch_number, storage_location, quality_status)
                VALUES (?, ?, 'g', ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                med_id, float(qty_val) if qty_val else 0, 
                float(price_val) if price_val else 0, 
                float(min_stock_val) if min_stock_val else 10, 
                row.get('purchase_date', ''), 
                row.get('expiry_date', ''), 
                row.get('supplier', ''), 
                row.get('batch_number', ''), 
                row.get('storage_location', ''), 
                row.get('quality_status', '合格')
            ))
        
        success += 1
        print(str(i) + " OK: " + name)
        
    except Exception as e:
        failed += 1
        print(str(i) + " FAIL: " + name + " - " + str(e))

conn.commit()

print("")
print("Import Complete!")
total = success + failed
print("Total: " + str(total) + ", Success: " + str(success) + ", Failed: " + str(failed))

if success == 100:
    print("")
    print("SUCCESS: All 100 medicines imported!")

conn.close()

print("")
print("Done!")

