
csv_file = "大药房库存录入模板_100味.csv"
fixed_file = "大药房库存录入模板_100味_fixed.csv"

print("Fixing CSV file...")

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

print("Original lines:", len(lines))

non_empty_lines = [line for line in lines if line.strip()]

print("Non-empty lines:", len(non_empty_lines))

with open(fixed_file, 'w', encoding='utf-8-sig') as f:
    f.writelines(non_empty_lines)

print("Fixed file written:", fixed_file)
print("\nNow let's verify:")

import csv

with open(fixed_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    print("Fieldnames:", reader.fieldnames)
    rows = list(reader)
    print("Number of rows:", len(rows))
    if rows:
        print("\nFirst row name:", rows[0].get('name', 'NONE'))

print("\nDone!")

