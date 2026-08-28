import ssl
import urllib.request
import urllib.parse
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cookie_processor = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), cookie_processor)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# 1. Fetch main page to obtain session cookie
main_url = "https://www.umucyo.gov.rw/pt/pcm/moveMainPageDetail.do"
req = urllib.request.Request(main_url, headers=headers)
resp = opener.open(req, timeout=15)
print(f"Main page fetched: {resp.status}")

# 2. Query Goods (G) tender advertising list
list_url = "https://www.umucyo.gov.rw/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G"
req = urllib.request.Request(list_url, headers=headers)
resp = opener.open(req, timeout=15)
html = resp.read().decode('utf-8', errors='ignore')
print(f"List page fetched: {resp.status}, HTML length: {len(html)}")

with open("scratch/umucyo_goods_list.html", "w", encoding="utf-8") as f:
    f.write(html)

# Extract table rows with regex
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
print(f"Found {len(rows)} table rows.")

tenders = []
for i, row in enumerate(rows):
    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
    clean_cells = [re.sub(r'<[^>]+>', ' ', c).strip() for c in cells]
    clean_cells = [' '.join(c.split()) for c in clean_cells]
    
    # Search for onclick or links
    onclick = re.findall(r'onclick=[\'"]([^\'"]+)[\'"]', row, re.IGNORECASE)
    
    if len(clean_cells) >= 4 and not clean_cells[0].lower().startswith("no"):
        print(f"\n--- Tender Row {i} ---")
        print(f"Cells: {clean_cells}")
        print(f"Onclick: {onclick}")
