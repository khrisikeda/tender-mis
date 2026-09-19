import re
import ssl
import time
import logging
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from app.services.ocds_service import (
    record_dead_letter,
    build_safe_portal_url,
    sync_ocds_tenders,
)

try:
    from sqlalchemy.orm import Session
    from app.models.tender import Tender, TenderItem, TenderSourceReference
    from app.models.tender_source import TenderSource
    from app.core.enums import TenderStatus
except ImportError:
    Session = None
    Tender = None
    TenderItem = None
    TenderSourceReference = None
    TenderSource = None
    TenderStatus = None

logger = logging.getLogger("umucyo_crawler")

UMUCYO_BASE_URL = "https://www.umucyo.gov.rw"
UMUCYO_MAIN_URL = f"{UMUCYO_BASE_URL}/pt/pcm/moveMainPageDetail.do"
UMUCYO_LIST_URL = f"{UMUCYO_BASE_URL}/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G"
UMUCYO_DETAIL_URL = f"{UMUCYO_BASE_URL}/eb/bav/selectAdvertisingDtlInfo.do"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Keywords to strictly filter for relevant medical, biomedical, clinical, laboratory, and hospital equipment
MEDICAL_KEYWORDS = [
    "medical equipment", "medical device", "biomedical", "patient monitor", "monitoring and critical",
    "vital signs", "ventilator", "radiology", "imaging", "pacs", "x-ray", "c-arm", "ct scanner",
    "ultrasound", "laboratory equipment", "clinical chemistry", "hematology", "analyzer", "reagents",
    "hospital equipment", "operating theatre", "surgical", "anesthesia", "infant warmer", "incubator",
    "phototherapy", "neonatal", "dialysis", "hemodialysis", "medical gas", "medical air compressor",
    "oxygen plant", "oxygen cylinder", "ophthalmology", "tonometer", "dental chair", "dental unit",
    "autoclave", "sterilizer", "defibrillator", "ecg", "suction machine", "tissue banking", "cornea",
    "metrology laborator", "hospital mattress", "mesical materials", "medical consumables"
]

EXCLUDED_CLIENTS = [
    "senate", "parliament", "kigali city", "district", "revenue authority", "rra",
    "edcl", "reg", "wasac", "police", "military", "rdf", "rwanda polytechnic",
    "court", "ombudsman", "minecofin", "mininfra", "rtda", "rura"
]

EXCLUDED_TITLE_KEYWORDS = [
    "security equipment", "security services", "genocide memorial", "vup program", "public works",
    "sport", "foot ball", "refreshment", "catering", "stationery", "stationaries", "printing",
    "solar home", "radio salus", "media production", "ict materials", "cleaning", "school",
    "curtain", "tea beverage", "water and tea", "seeds", "tractor", "plumbing", "jail", "court",
    "fire extinguisher", "road", "bridge", "office equipment", "cupboard", "locker safe", "cctv"
]


def _create_ssl_opener():
    """Creates a cookie-aware SSL opener for Umucyo."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    cookie_processor = urllib.request.HTTPCookieProcessor()
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), cookie_processor)


def parse_date_safe(date_str: str) -> Optional[datetime]:
    """Parse various date formats common in Umucyo (e.g. 28/09/2026 10:00, 2026-09-15 10:00)."""
    if not date_str:
        return None
    cleaned = re.sub(r'\(.*?\)', '', date_str).strip()
    formats = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def clean_html_text(text: str) -> str:
    """Removes HTML tags and normalizes whitespace."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('&nbsp;', ' ').replace('&#42;', '').replace('&amp;', '&')
    return ' '.join(text.split()).strip()


def parse_currency_amount(amount_str: str) -> Optional[float]:
    """Extracts numeric float value from currency strings (e.g. '34,643,704.51', '982,525.96 FRW')."""
    if not amount_str:
        return None
    cleaned = re.sub(r'[^\d.]', '', amount_str.replace(',', ''))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def is_relevant_medical_tender(title: str, client: Optional[str] = None) -> bool:
    """
    Filters tenders strictly for relevant medical, laboratory, hospital, and clinical equipment.
    Excludes non-medical clients (e.g. Senate, Kigali City, RRA) and non-medical titles.
    """
    if not title:
        return False
    title_lower = title.lower()
    client_lower = (client or "").lower()

    # Check excluded non-medical clients
    if client_lower and any(ex_client in client_lower for ex_client in EXCLUDED_CLIENTS):
        # Unless the tender title explicitly specifies hospital/medical equipment
        if not any(k in title_lower for k in ["medical equipment", "biomedical", "hospital equipment"]):
            return False

    # Exclude obvious non-medical items
    if any(ex in title_lower for ex in EXCLUDED_TITLE_KEYWORDS):
        return False

    # Check for direct medical keywords
    if any(k in title_lower for k in MEDICAL_KEYWORDS):
        return True

    # If from a recognized hospital / health institution with equipment
    if any(h in client_lower for h in ["hospital", "rbc", "biomedical", "health", "clinic"]):
        if any(w in title_lower for w in ["equipment", "machine", "device", "analyzer", "monitor", "oxygen"]):
            return True

    return False


def fetch_live_umucyo_tenders(max_pages: int = 5) -> List[Dict[str, Any]]:
    """
    Connects to Rwanda's Umucyo portal, scrapes multi-page advertised Goods notices,
    strictly filters for relevant medical & hospital equipment, and retrieves full lot breakdowns.
    """
    opener = _create_ssl_opener()

    # Step 1: Initialize session on main page
    try:
        req_main = urllib.request.Request(UMUCYO_MAIN_URL, headers=DEFAULT_HEADERS)
        opener.open(req_main, timeout=12)
    except Exception as e:
        logger.warning(f"Could not initialize session on main page: {e}")

    tenders_parsed = []
    seen_refs = set()

    for page in range(1, max_pages + 1):
        list_url = f"{UMUCYO_BASE_URL}/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G&currentPageNo={page}"
        try:
            req_list = urllib.request.Request(list_url, headers=DEFAULT_HEADERS)
            resp_list = opener.open(req_list, timeout=15)
            list_html = resp_list.read().decode('utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Error fetching page {page}: {e}")
            continue

        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', list_html, re.DOTALL | re.IGNORECASE)
        for row in rows:
            radio_match = re.search(r'<input\s+[^>]*name=[\'"]tenderNo[\'"][^>]*value=[\'"]([^\'"]+)[\'"]', row, re.IGNORECASE)
            if not radio_match:
                continue

            raw_val = radio_match.group(1)
            tokens = raw_val.split('|')
            if len(tokens) < 7:
                continue

            internal_ref_no = tokens[0]
            title_raw = tokens[1]
            tend_stage_cd = tokens[4] if len(tokens) > 4 else "O"
            tend_type_cd = tokens[6] if len(tokens) > 6 else "G"

            # Filter for relevant medical equipment ONLY
            client_hint = tokens[2] if len(tokens) > 2 else ""
            if not is_relevant_medical_tender(title_raw, client_hint):
                continue

            if internal_ref_no in seen_refs:
                continue
            seen_refs.add(internal_ref_no)

            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
            clean_cells = [clean_html_text(c) for c in cells]

            ref_no = clean_cells[2] if len(clean_cells) > 2 else internal_ref_no
            published_str = clean_cells[4] if len(clean_cells) > 4 else None
            deadline_str = clean_cells[5] if len(clean_cells) > 5 else None

            # Fetch detailed notice
            dtl_data = fetch_single_tender_detail(
                opener=opener,
                internal_ref_no=internal_ref_no,
                tend_stage_cd=tend_stage_cd,
                tend_type_cd=tend_type_cd,
            )
            safe_portal_url = build_safe_portal_url(adv_no=internal_ref_no, adv_status="00")

            t_title = dtl_data.get("title") or title_raw
            t_entity = dtl_data.get("procuring_entity") or client_hint or "Rwanda Biomedical Institution"

            if not is_relevant_medical_tender(t_title, t_entity):
                continue

            # Determine category
            cat = "Medical Equipment"
            t_lower = t_title.lower()
            if any(k in t_lower for k in ["radiology", "imaging", "x-ray", "c-arm", "ct scanner", "mri"]):
                cat = "Imaging & Radiology"
            elif any(k in t_lower for k in ["icu", "neonatal", "warmer", "incubator", "ventilator", "patient monitor", "monitoring"]):
                cat = "Neonatal & ICU"
            elif any(k in t_lower for k in ["laboratory", "biomed", "chemistry analyzer", "reagents", "metrology"]):
                cat = "Laboratory"
            elif any(k in t_lower for k in ["surgical", "operating theatre", "theatre", "suction"]):
                cat = "Surgical"
            elif any(k in t_lower for k in ["oxygen", "medical gas", "compressor"]):
                cat = "Medical Gas & Infrastructure"
            elif any(k in t_lower for k in ["ophthalmology", "cornea", "eye"]):
                cat = "Ophthalmology"
            elif any(k in t_lower for k in ["dialysis", "renal"]):
                cat = "Renal & Dialysis"
            elif any(k in t_lower for k in ["pacs", "emrs", "telemedicine"]):
                cat = "Digital Health & Telemedicine"
            elif any(k in t_lower for k in ["dental"]):
                cat = "Dental"
            elif any(k in t_lower for k in ["linen", "mattress", "uniform", "textile", "drapes"]):
                cat = "Healthcare Supplies"

            tender_dict = {
                "reference_number": dtl_data.get("ref_no") or ref_no,
                "portal_adv_no": internal_ref_no,
                "portal_adv_status": "00",
                "title": t_title,
                "procuring_entity": t_entity,
                "category": cat,
                "procurement_method": dtl_data.get("procurement_method") or "National Competitive Bidding",
                "published_at": parse_date_safe(published_str) or dtl_data.get("published_at") or datetime.now(timezone.utc),
                "deadline_at": parse_date_safe(deadline_str) or dtl_data.get("deadline_at") or (datetime.now(timezone.utc) + timedelta(days=30)),
                "tender_value": dtl_data.get("tender_security_amount"),
                "currency": "RWF",
                "description": dtl_data.get("description") or title_raw,
                "source_url": safe_portal_url,
                "items": dtl_data.get("items", []),
            }

            tenders_parsed.append(tender_dict)

    return tenders_parsed


def fetch_single_tender_detail(opener, internal_ref_no: str, tend_stage_cd: str = "O", tend_type_cd: str = "G") -> Dict[str, Any]:
    """
    POSTs to selectAdvertisingDtlInfo.do with exponential backoff and session header management
    to retrieve comprehensive tender specifications, lots, and Tender Security Amount.
    Never issues raw GET requests without mandatory parameters.
    """
    headers = {
        **DEFAULT_HEADERS,
        "Referer": UMUCYO_LIST_URL,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = urllib.parse.urlencode({
        "tendReferNo": internal_ref_no,
        "tendStageCd": tend_stage_cd,
        "tendTypeCd": tend_type_cd,
        "currentPageNo": "1",
        "searchConditions": "/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100&leftTopFlag=l&tendTypeCd=G",
    }).encode('utf-8')

    retries = 3
    delay = 1.0
    html = ""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(UMUCYO_DETAIL_URL, data=data, headers=headers)
            resp = opener.open(req, timeout=15)
            if resp.status != 200:
                record_dead_letter(
                    endpoint=UMUCYO_DETAIL_URL,
                    status_code=resp.status,
                    error_message=f"Non-200 detail response for {internal_ref_no}",
                    context={"internal_ref_no": internal_ref_no, "attempt": attempt + 1}
                )
                time.sleep(delay)
                delay *= 2
                continue
            html = resp.read().decode('utf-8', errors='ignore')
            break
        except urllib.error.HTTPError as e:
            record_dead_letter(
                endpoint=UMUCYO_DETAIL_URL,
                status_code=e.code,
                error_message=f"HTTPError: {e.reason}",
                context={"internal_ref_no": internal_ref_no, "attempt": attempt + 1}
            )
            if attempt == retries - 1:
                return {}
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            record_dead_letter(
                endpoint=UMUCYO_DETAIL_URL,
                status_code=None,
                error_message=f"Fetch detail error: {str(e)}",
                context={"internal_ref_no": internal_ref_no, "attempt": attempt + 1}
            )
            if attempt == retries - 1:
                return {}
            time.sleep(delay)
            delay *= 2

    if not html:
        return {}

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
    
    tender_name = None
    procuring_entity = None
    ref_no = None
    procurement_method = None
    deadline_at = None
    tender_security_amount = None
    items = []
    description_lines = []

    is_lot_table = False

    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
        clean = [clean_html_text(c) for c in cells if clean_html_text(c)]
        if not clean:
            continue

        row_text = " | ".join(clean)
        description_lines.append(row_text)

        if "Tender No" in clean[0] and len(clean) > 1:
            ref_no = clean[1]
        elif "Tender Name" in clean[0] and len(clean) > 1:
            tender_name = clean[1]
        elif "Procuring Entity" in clean[0] and len(clean) > 1:
            procuring_entity = clean[1].replace('-->', '').strip()
        elif "Tender Method" in clean:
            idx = clean.index("Tender Method")
            if idx + 1 < len(clean):
                procurement_method = clean[idx + 1]
        elif "Deadline for Bids Submission" in clean[0] and len(clean) > 1:
            deadline_at = parse_date_safe(clean[1])
        
        # Check for Tender Security across English, French, and portal terminology
        sec_markers = [
            "tender security",
            "bid security",
            "sum of lots",
            "garantie de soumission",
            "caution de soumission",
            "cautionnement provisoire",
        ]
        if any(marker in row_text.lower() for marker in sec_markers):
            amounts = re.findall(r'(?:RWF|FRW|\$)?\s*([\d]{1,3}(?:[,\s]\d{3})*(?:\.\d{1,2})?)', row_text)
            for amt in amounts:
                parsed_amt = parse_currency_amount(amt)
                if parsed_amt and parsed_amt >= 500:
                    tender_security_amount = parsed_amt
                    break

        if "LOT No" in row_text and "Name of Goods" in row_text:
            is_lot_table = True
            continue

        if is_lot_table:
            if clean and clean[0].isdigit() and len(clean) >= 3:
                lot_no = clean[0]
                lot_name = clean[1]
                lot_sec_amt = clean[2] if len(clean) > 2 else ""
                delivery_place = clean[4] if len(clean) > 4 else "Rwanda"
                
                items.append({
                    "description": f"Lot {lot_no}: {lot_name}",
                    "quantity": 1,
                    "unit": "Lot",
                    "specifications": {
                        "lot_number": lot_no,
                        "lot_name": lot_name,
                        "tender_security_amount": lot_sec_amt,
                        "delivery_place": delivery_place,
                    }
                })
            elif "Document Name" in row_text or "Required bidding" in row_text:
                is_lot_table = False

    # Fallback to sum of lots if header didn't specify total security
    if not tender_security_amount and items:
        total_lot_security = 0.0
        for itm in items:
            spec_sec = itm.get("specifications", {}).get("tender_security_amount", "")
            parsed_lot_amt = parse_currency_amount(spec_sec)
            if parsed_lot_amt:
                total_lot_security += parsed_lot_amt
        if total_lot_security > 0:
            tender_security_amount = total_lot_security

    return {
        "ref_no": ref_no,
        "title": tender_name,
        "procuring_entity": procuring_entity,
        "procurement_method": procurement_method,
        "deadline_at": deadline_at,
        "tender_security_amount": tender_security_amount,
        "description": "\n".join(description_lines[:25]),
        "items": items,
    }


async def sync_umucyo_tenders(db: Session, max_pages: int = 5) -> Dict[str, Any]:
    """
    Two-Tier Ingestion Orchestrator:
    - Tier 1: Primary Ingestion via Rwanda Official OCDS API (standardized releases & alerts).
    - Tier 2: Deep Retrieval / Fallback Scraper across Umucyo portal with safe URL parameters,
              session header management, exponential backoff, and dead-letter handling.
    """
    now = datetime.now(timezone.utc)
    source = db.query(TenderSource).filter(
        (TenderSource.name.ilike("%Umucyo%")) | (TenderSource.name.ilike("%RPPA%"))
    ).first()

    # Tier 1: Execute primary OCDS synchronization
    logger.info("Executing Tier 1 (Official OCDS API) synchronization...")
    ocds_report = sync_ocds_tenders(db=db, limit=50, query="medical")

    # Tier 2: Execute Fallback / Portal Deep Retrieval
    logger.info("Executing Tier 2 (Portal Deep Retrieval & Fallback) pass...")
    tenders_data = []
    is_live_extraction = False

    try:
        tenders_data = fetch_live_umucyo_tenders(max_pages=max_pages)
        if tenders_data:
            is_live_extraction = True
    except Exception as e:
        record_dead_letter(
            endpoint=UMUCYO_LIST_URL,
            status_code=None,
            error_message=f"Live Umucyo extraction exception: {str(e)}",
            context={"max_pages": max_pages}
        )
        logger.warning(f"Live Umucyo extraction encountered an issue ({e}). Returning live results only.")

    if not tenders_data:
        tenders_data = []

    # Deduplicate & upsert portal items
    portal_created_count = 0
    portal_updated_count = 0
    synced_summaries = []

    for item_data in tenders_data:
        ref = item_data.get("reference_number")
        if not ref:
            continue

        existing = db.query(Tender).filter(
            (Tender.reference_number == ref) | (Tender.portal_adv_no == item_data.get("portal_adv_no"))
        ).first()

        items_payload = item_data.pop("items", [])

        if existing:
            if item_data.get("deadline_at"):
                existing.deadline_at = item_data["deadline_at"]
            if item_data.get("tender_value"):
                existing.tender_value = item_data["tender_value"]
            if item_data.get("source_url"):
                existing.source_url = item_data["source_url"]
            if item_data.get("portal_adv_no"):
                existing.portal_adv_no = item_data["portal_adv_no"]
                existing.portal_adv_status = item_data.get("portal_adv_status", "00")
            existing.updated_at = now
            portal_updated_count += 1
            synced_summaries.append({
                "reference_number": existing.reference_number,
                "title": existing.title,
                "source_url": existing.source_url,
                "status": "updated",
            })
        else:
            new_tender = Tender(
                status=TenderStatus.NEW,
                country="Rwanda",
                **item_data
            )
            db.add(new_tender)
            db.flush()

            for item_dict in items_payload:
                db.add(TenderItem(tender_id=new_tender.id, **item_dict))

            if new_tender.source_url:
                db.add(TenderSourceReference(
                    tender_id=new_tender.id,
                    source_id=source.id if source else None,
                    source_url=new_tender.source_url,
                ))

            portal_created_count += 1
            synced_summaries.append({
                "reference_number": new_tender.reference_number,
                "title": new_tender.title,
                "source_url": new_tender.source_url,
                "status": "created",
            })

    # Update TenderSource health metrics
    if source:
        source.last_scan_at = now
        source.last_successful_scan_at = now
        source.tenders_collected_count = (source.tenders_collected_count or 0) + portal_created_count
        source.last_error = None
        db.add(source)

    db.commit()

    return {
        "strategy": "Two-Tier Resilient Ingestion",
        "tier1_ocds": ocds_report,
        "tier2_portal": {
            "source": "Umucyo e-Procurement (RPPA)",
            "is_live_extraction": is_live_extraction,
            "tenders_scanned": len(tenders_data),
            "new_tenders_created": portal_created_count,
            "tenders_updated": portal_updated_count,
            "sample_tenders": synced_summaries[:6],
        },
        "total_new_created": ocds_report["new_tenders_created"] + portal_created_count,
        "total_updated": ocds_report["tenders_updated"] + portal_updated_count,
        "synced_at": now.isoformat(),
    }
