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
    "Referer": "https://www.umucyo.gov.rw/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l",
    "Content-Type": "application/x-www-form-urlencoded",
}

# 1. Initialize session
req_main = urllib.request.Request("https://www.umucyo.gov.rw/pt/pcm/moveMainPageDetail.do", headers=headers)
opener.open(req_main, timeout=15)

# 2. Query pages 1 to 8 of Goods (G)
goods_tenders = []
for page in range(1, 9):
    url = f"https://www.umucyo.gov.rw/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G&currentPageNo={page}"
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = opener.open(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
        for row in rows:
            radio_match = re.search(r'<input\s+[^>]*name=[\'"]tenderNo[\'"][^>]*value=[\'"]([^\'"]+)[\'"]', row, re.IGNORECASE)
            if radio_match:
                tokens = radio_match.group(1).split('|')
                if len(tokens) >= 7:
                    goods_tenders.append({
                        "tendReferNo": tokens[0],
                        "title": tokens[1],
                        "buyer_code": tokens[2] if len(tokens) > 2 else "",
                        "date": tokens[3] if len(tokens) > 3 else "",
                        "tendStageCd": tokens[4] if len(tokens) > 4 else "O",
                        "method": tokens[5] if len(tokens) > 5 else "",
                        "tendTypeCd": tokens[6] if len(tokens) > 6 else "G",
                        "deadline": tokens[7] if len(tokens) > 7 else "",
                    })
    except Exception as e:
        print(f"Error on page {page}: {e}")

print(f"Total Goods Tenders Scanned: {len(goods_tenders)}")

# Filter for healthcare / medical / biological / clinical / hospital / diagnostic / pharmacy / lab / equipment
keywords = ["patient", "medical", "hospital", "equipment", "health", "care", "diagnostic", "clinic", "lab", "oxygen", "first-aid", "emrs", "imaging", "monitor", "frigo", "ambulance", "reagent", "pharma", "biomedical"]

relevant = [t for t in goods_tenders if any(k in t["title"].lower() for k in keywords)]
print(f"Found {len(relevant)} relevant medical/healthcare equipment tenders:")

for idx, r in enumerate(relevant):
    print(f"{idx+1}. [{r['tendReferNo']}] {r['title']} | Method: {r['method']} | Deadline: {r['deadline']}")

with open("scratch/relevant_medical_goods.json", "w", encoding="utf-8") as f:
    json.dump(relevant, f, indent=2)
