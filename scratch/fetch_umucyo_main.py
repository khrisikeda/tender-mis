import sys
import ssl
import urllib.request
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

for u in [
    "https://www.umucyo.gov.rw/",
    "https://www.umucyo.gov.rw/pt/pcm/moveMainPageDetail.do",
]:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"=== [{resp.status}] {u} (Length: {len(html)}) ===")
            # Look for forms, inputs, scripts, urls
            links = re.findall(r'[\'"](/[^/][^\'"]*\.do[^\'"]*)[\'"]', html)
            print("Found endpoints:", set(links))
            with open(f"scratch/page_{u.split('/')[-1] or 'root'}.html", "w", encoding="utf-8") as f:
                f.write(html)
    except Exception as e:
        print(f"[FAIL] {u} -> {e}")
