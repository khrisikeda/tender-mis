import re

with open("scratch/umucyo_goods_list.html", "r", encoding="utf-8") as f:
    html = f.read()

view_detail = re.findall(r'function\s+ViewDetail\s*\([^)]*\)\s*\{[^}]+\}', html, re.DOTALL)
print("ViewDetail function:", view_detail)

forms = re.findall(r'<form\s+[^>]*name=[\'"]([^\'"]+)[\'"][^>]*action=[\'"]([^\'"]+)[\'"][^>]*>', html)
print("Forms found:", forms)
