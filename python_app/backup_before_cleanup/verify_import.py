
import sqlite3

db_file = "medicine_system.db"

print("=" * 60)
print("   Import Verification")
print("=" * 60)

conn = sqlite3.connect(db_file)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM medicines")
med_count = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM inventory")
inv_count = c.fetchone()[0]

print("\n统计:")
print("  药材数量:", med_count)
print("  库存记录:", inv_count)

if med_count &gt;= 98:
    print("\n✓ 验证通过！导入成功！")
else:
    print("\n⚠  数据可能不完整")

print("\n前10味药材:")
c.execute("SELECT name, category, origin FROM medicines ORDER BY id LIMIT 10")
for idx, row in enumerate(c.fetchall()):
    print("  " + str(idx+1) + ". " + row[0] + " (" + str(row[1]) + ") - " + str(row[2]))

print("\n库存示例:")
c.execute('''
    SELECT m.name, i.quantity, i.price, i.quality_status 
    FROM medicines m 
    JOIN inventory i ON m.id = i.medicine_id 
    LIMIT 5
''')
for row in c.fetchall():
    print("  " + str(row[0]) + ": " + str(row[1]) + "g, ￥" + str(row[2]) + ", " + str(row[3]))

conn.close()

print("\n" + "=" * 60)
print("Done!")

