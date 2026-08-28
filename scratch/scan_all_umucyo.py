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

# 1. Main session
req_main = urllib.request.Request("https://www.umucyo.gov.rw/pt/pcm/moveMainPageDetail.do", headers=headers)
opener.open(req_main, timeout=15)

# 2. Fetch all pages of Goods (G) and Non-Consultant (NC)
all_found = []

for tender_type in ['G', 'NC']:
    for page_no in range(1, 4):
        url = f"https://www.umucyo.gov.rw/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd={tender_type}&currentPageNo={page_no}"
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = opener.open(req, timeout=15)
            html = resp.read().decode('utf-8', errors='ignore')
            
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
            for row in rows:
                radio_match = re.search(r'<input\s+[^>]*name=[\'"]tenderNo[\'"][^>]*value=[\'"]([^\'"]+)[\'"]', row, re.IGNORECASE)
                if radio_match:
                    raw_val = radio_match.group(1)
                    tokens = raw_val.split('|')
                    if len(tokens) >= 7:
                        all_found.append({
                            "tendReferNo": tokens[0],
                            "title": tokens[1],
                            "buyer_code": tokens[2] if len(tokens) > 2 else "",
                            "date": tokens[3] if len(tokens) > 3 else "",
                            "tendStageCd": tokens[4] if len(tokens) > 4 else "O",
                            "method": tokens[5] if len(tokens) > 5 else "",
                            "tendTypeCd": tokens[6] if len(tokens) > 6 else tender_type,
                            "deadline": tokens[7] if len(tokens) > 7 else "",
                        })
        except Exception as e:
            print(f"Error on type {tender_type} page {page_no}: {e}")

print(f"Total tenders found across pages: {len(all_found)}")
for i, t in enumerate(all_found):
    print(f"{i+1}. [{t['tendReferNo']}] {t['title']} | Type: {t['tendTypeCd']} | Method: {t['method']} | Deadline: {t['deadline']}")
