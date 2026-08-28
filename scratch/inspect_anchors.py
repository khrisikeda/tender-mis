import re

with open("scratch/umucyo_goods_list.html", "r", encoding="utf-8") as f:
    html = f.read()

# find all anchor tags in table
anchors = re.findall(r'<a\s+[^>]*href=[^>]*>.*?</a>', html, re.DOTALL | re.IGNORECASE)
print(f"Total anchors: {len(anchors)}")

for a in anchors[:15]:
    print("ANCHOR:", a)
