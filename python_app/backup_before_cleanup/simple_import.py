
import sys
import os
import sqlite3

csv_file = "大药房库存录入模板_100味.csv"
db_file = "medicine_system.db"

print("=" * 60)
print("   Simple Import Tool")
print("=" * 60)

if not os.path.exists(csv_file):
    print("ERROR: File not found")
    sys.exit(1)

print("\nFile found")
print("Connecting to database...")

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print("Database connected")
print("\nReading CSV file...")

lines = []
with open(csv_file, 'r', encoding='utf-8-sig') as f:
    for line in f:
        lines.append(line.strip())

if len(lines) &lt; 2:
    print("ERROR: CSV file is empty")
    sys.exit(1)

header_line = lines[0]
headers = [h.strip() for h in header_line.split(',')]

print("Headers found: " + str(len(headers)))
print("\nProcessing data...")

success = 0
failed = 0

for i in range(1, len(lines)):
    line = lines[i]
    if not line:
        continue
    
    values = []
    current = ''
    in_quotes = False
    
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            values.append(current.strip())
            current = ''
        else:
            current += char
    
    values.append(current.strip())
    
    while len(values) &lt; len(headers):
        values.append('')
    
    row = {}
    for j in range(min(len(headers), len(values))):
        row[headers[j]] = values[j]
    
    row_num = i
    name = row.get('name', '')
    
    try:
        if not name:
            print("Row " + str(row_num) + " - No name, skipping")
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
                try:
                    new_qty = float(current_qty) + float(qty_val)
                except:
                    new_qty = float(current_qty)
                
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
        print("[" + str(row_num) + "/100] OK: " + name)
        
    except Exception as e:
        failed += 1
        print("[" + str(row_num) + "/100] FAIL: " + name)
        print("  Error: " + str(e))

conn.commit()

print("\n" + "=" * 60)
print("Import Complete!")
total = success + failed
print("Total: " + str(total) + ", Success: " + str(success) + ", Failed: " + str(failed))

if success == 100:
    print("\nSUCCESS: All 100 medicines imported!")

conn.close()

print("\nDone!")

