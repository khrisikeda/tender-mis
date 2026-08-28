import re

with open("scratch/umucyo_goods_list.html", "r", encoding="utf-8") as f:
    html = f.read()

rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
print(f"Total rows: {len(rows)}")

for i in range(7, min(12, len(rows))):
    print(f"\n--- ROW {i} RAW HTML ---")
    print(rows[i])
