
import sqlite3

conn = sqlite3.connect('medicine_system.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM medicines')
med_count = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM inventory')
inv_count = c.fetchone()[0]

print('Medicine count:', med_count)
print('Inventory count:', inv_count)

print('\nFirst 5 medicines:')
c.execute('SELECT name, category FROM medicines LIMIT 5')
for row in c.fetchall():
    print('  -', row[0], '(', row[1], ')')

conn.close()

