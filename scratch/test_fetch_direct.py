import sys
import os
sys.path.insert(0, os.path.abspath("."))
import json
from app.services.umucyo_crawler import fetch_live_umucyo_tenders

print("Testing fetch_live_umucyo_tenders()...")
tenders = fetch_live_umucyo_tenders(max_items=3)
print(f"\nExtracted {len(tenders)} live tenders from Umucyo:")

for i, t in enumerate(tenders):
    print(f"\n--- TENDER {i+1} ---")
    print(f"Ref: {t['reference_number']}")
    print(f"Title: {t['title']}")
    print(f"Entity: {t['procuring_entity']}")
    print(f"Method: {t['procurement_method']}")
    print(f"Tender Security Amount (RWF): {t['tender_value']:,} RWF" if t['tender_value'] else "Tender Security Amount: N/A")
    print(f"Deadline: {t['deadline_at']}")
    print(f"Source URL: {t['source_url']}")
    print(f"Items/Lots ({len(t['items'])}):")
    for item in t['items'][:4]:
        specs = item.get('specifications', {})
        print(f"  * {item['description']} -> Security: {specs.get('tender_security_amount')} | Delivery: {specs.get('delivery_place')}")
