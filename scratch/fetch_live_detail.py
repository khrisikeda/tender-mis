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
    "Referer": "https://www.umucyo.gov.rw/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G",
    "Content-Type": "application/x-www-form-urlencoded",
}

# 1. Fetch main page to obtain session cookie
main_url = "https://www.umucyo.gov.rw/pt/pcm/moveMainPageDetail.do"
req = urllib.request.Request(main_url, headers=headers)
resp = opener.open(req, timeout=15)
print(f"Main page fetched: {resp.status}")

# 2. POST to selectAdvertisingDtlInfo.do
dtl_url = "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingDtlInfo.do"
data = urllib.parse.urlencode({
    "tendReferNo": "000003/G/ICB/2026/2027/1605000000",
    "tendStageCd": "O",
    "tendTypeCd": "G",
    "currentPageNo": "1",
    "searchConditions": "/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G",
}).encode('utf-8')

req = urllib.request.Request(dtl_url, data=data, headers=headers)
resp = opener.open(req, timeout=20)
html = resp.read().decode('utf-8', errors='ignore')
print(f"Detail page fetched: {resp.status}, HTML length: {len(html)}")

with open("scratch/umucyo_detail_sample.html", "w", encoding="utf-8") as f:
    f.write(html)

# Extract table rows
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
print(f"Detail rows: {len(rows)}")

for i, row in enumerate(rows):
    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
    clean_cells = [re.sub(r'<[^>]+>', ' ', c).strip() for c in cells]
    clean_cells = [' '.join(c.split()) for c in clean_cells if c.strip()]
    if clean_cells:
        print(f"Row {i}: {clean_cells}")
