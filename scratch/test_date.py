import sys
import os
sys.path.insert(0, os.path.abspath("."))

from app.services.umucyo_crawler import parse_date_safe

test_dates = [
    "28/09/2026 10:00 (local time)",
    "28/09/2026 11:00 (local time)",
    "28/09/2026 10:00",
    "25/08/2026",
    "2026-09-28 10:00:00",
    "28-09-2026 10:00"
]

for d in test_dates:
    res = parse_date_safe(d)
    print(f"Raw: '{d}' -> Parsed: {res} (ISO: {res.isoformat() if res else 'None'})")
