import sys
import ssl
import urllib.request
import re

urls_to_test = [
    "https://www.umucyo.gov.rw/",
    "https://www.umucyo.gov.rw/index.do",
    "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingList.do",
    "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingDtlInfo.do",
    "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingListAll.do",
    "https://www.umucyo.gov.rw/eb/bav/selectNoticeList.do",
    "https://www.umucyo.gov.rw/ep/inv/selectBidPlanList.do"
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

for u in urls_to_test:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"[{resp.status}] {u} (Length: {len(html)})")
            # find any .do links in html
            links = re.findall(r'href=[\'"]([^\'"]+\.do[^\'"]*)[\'"]', html)
            action_links = re.findall(r'action=[\'"]([^\'"]+\.do[^\'"]*)[\'"]', html)
            onclick_links = re.findall(r'[\'"](/[^\'"]+\.do[^\'"]*)[\'"]', html)
            found = set(links + action_links + onclick_links)
            if found:
                print(f"   Found {len(found)} .do links: {list(found)[:8]}")
    except Exception as e:
        print(f"[FAIL] {u} -> {e}")
