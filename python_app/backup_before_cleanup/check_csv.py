
import csv

csv_file = "大药房库存录入模板_100味.csv"

print("Checking CSV file...")

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

print("Total lines:", len(lines))
print("\nLine 1 (header):")
print(repr(lines[0]))

print("\nLine 2:")
print(repr(lines[1]))

print("\n--- Using csv.DictReader ---")
with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    print("Fieldnames:", reader.fieldnames)
    rows = list(reader)
    print("Number of rows:", len(rows))
    if rows:
        print("\nFirst row keys:", list(rows[0].keys()))
        print("\nFirst row:", rows[0])

