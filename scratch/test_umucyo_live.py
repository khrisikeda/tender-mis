import sys
import ssl
import json
import urllib.request
import urllib.parse
from html.parser import HTMLParser

url = "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingList.do"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
        print(f"STATUS: {response.status}")
        print(f"HTML Length: {len(html)}")
        print("HTML snippet (first 1000 chars):")
        print(html[:1000])
        
        with open("scratch/umucyo_sample.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved to scratch/umucyo_sample.html")
except Exception as e:
    print(f"ERROR: {e}")
