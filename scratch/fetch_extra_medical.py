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

# Main session
req_main = urllib.request.Request("https://www.umucyo.gov.rw/pt/pcm/moveMainPageDetail.do", headers=headers)
opener.open(req_main, timeout=15)

extra_targets = [
    {"tendReferNo": "000004/G/NCB/2026/2027/6300003001", "tendStageCd": "O", "tendTypeCd": "G", "title": "Supply and installation od Medical Air Compressor for ICU and Neonatalogy"},
    {"tendReferNo": "000002/G/NCB/2026/2027/6500003002", "tendStageCd": "O", "tendTypeCd": "G", "title": "Supply of Medical Equipment"},
    {"tendReferNo": "000003/G/NCB/2026/2027/1806000000", "tendStageCd": "O", "tendTypeCd": "G", "title": "Provision of Personal Protective Equipment (PPEs)"},
]

def clean_text(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', ' ', text).replace('&nbsp;', ' ').replace('&#42;', '').replace('&amp;', '&')
    return ' '.join(text.split()).strip()

extra_results = []
for t in extra_targets:
    dtl_url = "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingDtlInfo.do"
    data = urllib.parse.urlencode({
        "tendReferNo": t["tendReferNo"],
        "tendStageCd": t["tendStageCd"],
        "tendTypeCd": t["tendTypeCd"],
        "currentPageNo": "1",
        "searchConditions": f"/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd={t['tendTypeCd']}",
    }).encode('utf-8')

    try:
        req = urllib.request.Request(dtl_url, data=data, headers=headers)
        resp = opener.open(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
        info = {
            "ref_internal": t["tendReferNo"],
            "title": t["title"],
            "entity": None,
            "ref_no": None,
            "deadline": None,
            "opening": None,
            "tender_security": None,
            "fee": None,
            "method": None,
            "lots": []
        }
        
        is_lot = False
        for r in rows:
            cells = [clean_text(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL | re.IGNORECASE)]
            cells = [c for c in cells if c]
            if not cells: continue
            line = " | ".join(cells)
            
            if "Tender No" in cells[0] and len(cells) > 1:
                info["ref_no"] = cells[1]
            if "Procuring Entity" in cells[0] and len(cells) > 1:
                info["entity"] = cells[1].replace('-->', '').strip()
            if "Tender Name" in cells[0] and len(cells) > 1:
                info["title"] = cells[1]
            if "Tender Method" in cells:
                idx = cells.index("Tender Method")
                if idx + 1 < len(cells): info["method"] = cells[idx+1]
            if "Deadline for Bids Submission" in cells[0] and len(cells) > 1:
                info["deadline"] = cells[1]
            if "Opening Date" in cells[0] and len(cells) > 1:
                info["opening"] = cells[1]
            if "Tender Fee" in cells[0] and len(cells) > 1:
                info["fee"] = cells[1]
            if "Tender Security (sum of LOTs)" in line or "Tender Security Amount" in line:
                for token in re.findall(r'[\d,]+\.?\d*', line):
                    val = token.replace(',', '')
                    if val.replace('.', '').isdigit() and float(val) > 1000:
                        info["tender_security"] = float(val)
                        break
            
            if "LOT No" in line and "Name of Goods" in line:
                is_lot = True
                continue
            if is_lot:
                if cells[0].isdigit() and len(cells) >= 3:
                    info["lots"].append({
                        "lot_no": cells[0],
                        "name": cells[1],
                        "security": cells[2] if len(cells) > 2 else "",
                        "delivery_time": cells[3] if len(cells) > 3 else "",
                        "place": cells[4] if len(cells) > 4 else ""
                    })
                elif "Document Name" in line:
                    is_lot = False
        
        extra_results.append(info)
    except Exception as e:
        print(f"Error fetching {t['tendReferNo']}: {e}")

print(json.dumps(extra_results, indent=2))
