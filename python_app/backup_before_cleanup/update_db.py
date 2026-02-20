
import sqlite3

db_file = "medicine_system.db"

print("Updating database schema...")

conn = sqlite3.connect(db_file)
c = conn.cursor()

c.execute("PRAGMA table_info(medicines)")
cols = [col[1] for col in c.fetchall()]
print("Medicines columns:", cols)

if "origin" not in cols:
    print("Adding origin column...")
    c.execute("ALTER TABLE medicines ADD COLUMN origin TEXT")

if "grade" not in cols:
    print("Adding grade column...")
    c.execute("ALTER TABLE medicines ADD COLUMN grade TEXT")

c.execute("PRAGMA table_info(inventory)")
cols = [col[1] for col in c.fetchall()]
print("Inventory columns:", cols)

if "purchase_date" not in cols:
    print("Adding purchase_date column...")
    c.execute("ALTER TABLE inventory ADD COLUMN purchase_date TEXT")

if "expiry_date" not in cols:
    print("Adding expiry_date column...")
    c.execute("ALTER TABLE inventory ADD COLUMN expiry_date TEXT")

if "supplier" not in cols:
    print("Adding supplier column...")
    c.execute("ALTER TABLE inventory ADD COLUMN supplier TEXT")

if "batch_number" not in cols:
    print("Adding batch_number column...")
    c.execute("ALTER TABLE inventory ADD COLUMN batch_number TEXT")

if "storage_location" not in cols:
    print("Adding storage_location column...")
    c.execute("ALTER TABLE inventory ADD COLUMN storage_location TEXT")

if "quality_status" not in cols:
    print("Adding quality_status column...")
    c.execute("ALTER TABLE inventory ADD COLUMN quality_status TEXT DEFAULT '合格'")

conn.commit()
conn.close()

print("")
print("Database schema updated!")

