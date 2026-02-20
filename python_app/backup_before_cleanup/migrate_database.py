
import sqlite3
import shutil
from datetime import datetime

print("=" * 60)
print("   Database Migration Tool")
print("=" * 60)

db_file = 'medicine_system.db'
backup_file = 'medicine_system_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.db'

print("\nStep 1: Creating backup...")
shutil.copy2(db_file, backup_file)
print("Backup created:", backup_file)

print("\nStep 2: Connecting to database...")
conn = sqlite3.connect(db_file)
c = conn.cursor()

print("\nStep 3: Creating new simplified tables...")

c.execute('''
    CREATE TABLE IF NOT EXISTS medicines_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        alias TEXT,
        category TEXT,
        nature TEXT,
        taste TEXT,
        meridian TEXT,
        efficacy TEXT,
        indications TEXT,
        usage TEXT,
        dosage TEXT,
        contraindication TEXT,
        notes TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS inventory_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        quantity REAL NOT NULL DEFAULT 0,
        unit TEXT DEFAULT 'g',
        price REAL NOT NULL DEFAULT 0,
        min_stock REAL DEFAULT 0,
        FOREIGN KEY (medicine_id) REFERENCES medicines_new (id)
    )
''')

print("New tables created")

print("\nStep 4: Migrating data...")

c.execute('''
    INSERT INTO medicines_new (id, name, alias, category, nature, taste, meridian, 
                               efficacy, indications, usage, dosage, contraindication, notes)
    SELECT id, name, alias, category, nature, taste, meridian, 
           efficacy, indications, usage, dosage, contraindication, notes
    FROM medicines
''')
med_count = c.rowcount
print("Migrated", med_count, "medicine records")

c.execute('''
    INSERT INTO inventory_new (id, medicine_id, quantity, unit, price, min_stock)
    SELECT id, medicine_id, quantity, unit, price, min_stock
    FROM inventory
''')
inv_count = c.rowcount
print("Migrated", inv_count, "inventory records")

print("\nStep 5: Dropping old tables...")

c.execute('DROP TABLE inventory')
c.execute('DROP TABLE medicines')

print("Old tables dropped")

print("\nStep 6: Renaming new tables...")

c.execute('ALTER TABLE medicines_new RENAME TO medicines')
c.execute('ALTER TABLE inventory_new RENAME TO inventory')

print("Tables renamed")

print("\nStep 7: Recreating indexes...")

c.execute('CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines (name)')
c.execute('CREATE INDEX IF NOT EXISTS idx_medicines_category ON medicines (category)')
c.execute('CREATE INDEX IF NOT EXISTS idx_inventory_medicine_id ON inventory (medicine_id)')

print("Indexes created")

conn.commit()

print("\nStep 8: Verifying migration...")

c.execute('SELECT COUNT(*) FROM medicines')
new_med_count = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM inventory')
new_inv_count = c.fetchone()[0]

print("\nNew table structure:")

print("\n[medicines] table columns:")
c.execute("PRAGMA table_info(medicines)")
for col in c.fetchall():
    print("  -", col[1], ":", col[2])

print("\n[inventory] table columns:")
c.execute("PRAGMA table_info(inventory)")
for col in c.fetchall():
    print("  -", col[1], ":", col[2])

conn.close()

print("\n" + "=" * 60)
print("Migration Complete!")
print("=" * 60)
print("\nSummary:")
print("  - Medicines:", new_med_count, "records")
print("  - Inventory:", new_inv_count, "records")
print("  - Backup file:", backup_file)
print("\nFields retained:")
print("  medicines: name, alias, category, nature, taste, meridian,")
print("             efficacy, indications, usage, dosage, contraindication, notes")
print("  inventory: quantity, unit, price, min_stock")
print("\nFields removed:")
print("  medicines: source, created_at, updated_at, origin, grade")
print("  inventory: last_updated, purchase_date, expiry_date, supplier,")
print("             batch_number, storage_location, quality_status")
print("=" * 60)

