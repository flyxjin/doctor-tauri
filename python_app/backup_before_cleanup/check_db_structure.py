
import sqlite3

conn = sqlite3.connect('medicine_system.db')
c = conn.cursor()

print("=" * 60)
print("   Current Database Structure")
print("=" * 60)

print("\n[medicines] table columns:")
c.execute("PRAGMA table_info(medicines)")
for col in c.fetchall():
    print("  -", col[1], ":", col[2])

print("\n[inventory] table columns:")
c.execute("PRAGMA table_info(inventory)")
for col in c.fetchall():
    print("  -", col[1], ":", col[2])

print("\n[medicines] sample data:")
c.execute("SELECT * FROM medicines LIMIT 1")
row = c.fetchone()
if row:
    c.execute("PRAGMA table_info(medicines)")
    cols = [col[1] for col in c.fetchall()]
    for i, col in enumerate(cols):
        if i < len(row):
            print("  ", col, "=", row[i])

print("\n[inventory] sample data:")
c.execute("SELECT * FROM inventory LIMIT 1")
row = c.fetchone()
if row:
    c.execute("PRAGMA table_info(inventory)")
    cols = [col[1] for col in c.fetchall()]
    for i, col in enumerate(cols):
        if i < len(row):
            print("  ", col, "=", row[i])

conn.close()

print("\n" + "=" * 60)
