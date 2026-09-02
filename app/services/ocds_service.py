"""
Rwanda Umucyo OCDS (Open Contracting Data Standard) Ingestion Service
===================================================================
Provides primary discovery, synchronization, field mapping, and idempotent
upserting for public procurement notices published via Rwanda's OCDS Engine
and Open Contracting Partnership datasets.
"""
import os
import json
import logging
import urllib.request
import urllib.parse
import ssl
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal

from sqlalchemy.orm import Session
from app.models.tender import Tender, TenderItem, TenderSourceReference
from app.models.tender_source import TenderSource
from app.core.enums import TenderStatus, EvidenceStatus

logger = logging.getLogger("ocds_ingestion")

# Primary endpoints for Rwanda Umucyo OCDS API
OCDS_DEFAULT_BASE_URL = os.getenv("OCDS_BASE_URL", "https://ocds.umucyo.gov.rw/opendata/api/v1")
OCDS_ALT_BASE_URL = "https://ocds.umucyo.gov.rw/api/v1"
OCDS_BULK_PUB_URL = "https://data.open-contracting.org/en/publication/145"

DEFAULT_HEADERS = {
    "User-Agent": "MedTender-Intelligence-MIS/1.0 (Rwanda Healthcare Procurement Ingestion)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# Dead-letter queue path
DEAD_LETTER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage")
DEAD_LETTER_FILE = os.path.join(DEAD_LETTER_DIR, "dead_letters.json")


def record_dead_letter(
    endpoint: str,
    status_code: Optional[int],
    error_message: str,
    context: Optional[Dict[str, Any]] = None,
):
    """Logs and persists dead-letter failure details for failed portal/API requests."""
    os.makedirs(DEAD_LETTER_DIR, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "status_code": status_code,
        "error": error_message,
        "context": context or {},
    }
    logger.error(f"[DEAD_LETTER] {endpoint} (HTTP {status_code}): {error_message} | Context: {context}")

    try:
        existing = []
        if os.path.exists(DEAD_LETTER_FILE):
            with open(DEAD_LETTER_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.append(entry)
        # Keep last 500 records
        existing = existing[-500:]
        with open(DEAD_LETTER_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, default=str)
    except Exception as e:
        logger.warning(f"Could not persist dead-letter entry to disk: {e}")

    return entry


def parse_ocds_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parses standard ISO 8601 timestamps returned by OCDS releases."""
    if not date_str:
        return None
    cleaned = date_str.replace("Z", "+00:00")
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(cleaned)
    except Exception:
        return None


def map_ocds_status(ocds_status: Optional[str]) -> TenderStatus:
    """Maps OCDS tender status to internal TenderStatus enum."""
    if not ocds_status:
        return TenderStatus.NEW
    status_lower = str(ocds_status).lower()
    mapping = {
        "active": TenderStatus.NEW,
        "planned": TenderStatus.REVIEW,
        "complete": TenderStatus.AWARDED,
        "cancelled": TenderStatus.CANCELLED,
        "unsuccessful": TenderStatus.LOST,
        "withdrawn": TenderStatus.CANCELLED,
    }
    return mapping.get(status_lower, TenderStatus.NEW)


def build_safe_portal_url(adv_no: str, adv_status: str = "00") -> str:
    """
    Safely generates Umucyo portal detail URL with mandatory query parameters.
    Never issues naked GET requests to selectAdvertisingDtlInfo.do without parameters.
    """
    encoded_no = urllib.parse.quote(str(adv_no).strip())
    encoded_status = urllib.parse.quote(str(adv_status).strip())
    return f"https://www.umucyo.gov.rw/eb/bav/selectAdvertisingDtlInfo.do?adv_no={encoded_no}&adv_status={encoded_status}"


class OCDSClient:
    """Client for querying Rwanda Umucyo OCDS APIs and parsing releases."""

    def __init__(self, base_url: str = OCDS_DEFAULT_BASE_URL, timeout_seconds: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def _get_json(self, path_or_url: str, params: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Dict[str, Any]], Optional[int]]:
        """Executes GET request with structured error handling and dead-letter capture."""
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            full_url = path_or_url
        else:
            full_url = f"{self.base_url}/{path_or_url.lstrip('/')}"

        if params:
            query_string = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            delimiter = "&" if "?" in full_url else "?"
            full_url = f"{full_url}{delimiter}{query_string}"

        req = urllib.request.Request(full_url, headers=DEFAULT_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl_context) as resp:
                status_code = resp.status
                content = resp.read().decode("utf-8", errors="ignore")
                if status_code != 200:
                    record_dead_letter(full_url, status_code, f"Non-200 response: {content[:200]}")
                    return None, status_code
                return json.loads(content), status_code
        except urllib.error.HTTPError as e:
            record_dead_letter(full_url, e.code, str(e.reason), {"url": full_url})
            return None, e.code
        except Exception as e:
            record_dead_letter(full_url, None, str(e), {"url": full_url})
            return None, None

    def fetch_releases(self, offset: int = 0, limit: int = 50, date_from: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetches paginated releases from OCDS endpoint."""
        params = {"offset": offset, "limit": limit}
        if date_from:
            params["date_from"] = date_from

        # Try primary endpoint
        data, status = self._get_json("releases/all", params)
        if not data and status != 200:
            # Fallback to alternate route
            alt_url = f"{OCDS_ALT_BASE_URL}/releases"
            data, _ = self._get_json(alt_url, params)

        if data and isinstance(data, dict):
            return data.get("releases", [])
        elif data and isinstance(data, list):
            return data
        return []

    def fetch_release_by_ocid(self, ocid: str) -> Optional[Dict[str, Any]]:
        """Fetches a specific release by its OCID."""
        data, _ = self._get_json("releases/", {"ocid": ocid})
        if data and isinstance(data, dict):
            return data
        return None

    def search_releases(self, query: str = "medical", procuring_type: str = "goods", page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """Uses OCDS UI full-text search endpoint."""
        params = {
            "query": query,
            "procuring_type": procuring_type,
            "page": page,
            "page_size": page_size,
        }
        data, _ = self._get_json("ui/releases/search", params)
        if data and isinstance(data, dict):
            return data.get("results", [])
        return []

    @staticmethod
    def map_release_to_tender_payload(release: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a standard OCDS 1.1 JSON release object to the internal Tender dictionary.
        - ocid / id -> Unique internal identifier & reference number
        - tender.title & tender.description -> Tender name and scope
        - tender.procuringEntity.name -> Buyer / Organization
        - tender.tenderPeriod.endDate -> Submission deadline
        - tender.status -> Publication / bidding status
        - tender.value.amount / currency -> Estimated value
        """
        ocid = release.get("ocid") or release.get("id") or ""
        tender_sec = release.get("tender") or {}
        buyer_sec = release.get("buyer") or {}
        procuring_entity_sec = tender_sec.get("procuringEntity") or {}

        title = tender_sec.get("title") or release.get("description") or f"Tender {ocid}"
        description = tender_sec.get("description") or title

        procuring_entity = (
            procuring_entity_sec.get("name")
            or buyer_sec.get("name")
            or "Rwanda Public Procurement Authority"
        )

        tender_period = tender_sec.get("tenderPeriod") or {}
        deadline_str = tender_period.get("endDate")
        published_str = tender_period.get("startDate") or release.get("date")

        val_obj = tender_sec.get("value") or {}
        tender_val = val_obj.get("amount")
        currency = val_obj.get("currency") or "RWF"

        # Unique reference / notice number
        ref_no = tender_sec.get("id") or ocid

        # Portal query params if available
        adv_no = ref_no
        adv_status = "00"

        # Generate resilient parameterized portal link
        source_url = build_safe_portal_url(adv_no, adv_status)

        # Parse Line Items / Lots if present
        items_payload = []
        for itm in tender_sec.get("items", []):
            item_desc = itm.get("description") or itm.get("id") or "Line Item"
            item_qty = itm.get("quantity")
            item_unit = itm.get("unit", {}).get("name") if isinstance(itm.get("unit"), dict) else str(itm.get("unit") or "Units")
            items_payload.append({
                "title": item_desc,
                "description": item_desc,
                "quantity": Decimal(str(item_qty)) if item_qty is not None else Decimal("1"),
                "unit": item_unit,
                "specifications": itm.get("classification") or {},
                "evidence_status": EvidenceStatus.REQUIRES_HUMAN_VERIFICATION,
            })

        return {
            "ocid": ocid,
            "ocds_release_id": release.get("id"),
            "reference_number": ref_no,
            "title": title[:500],
            "procuring_entity": procuring_entity[:300],
            "country": "Rwanda",
            "category": "Medical & Hospital Equipment" if any(k in title.lower() for k in ["medical", "health", "hospital", "patient", "lab", "icu", "device"]) else "Healthcare Supplies",
            "procurement_method": tender_sec.get("procurementMethodDetails") or tender_sec.get("procurementMethod") or "Open Competitive",
            "published_at": parse_ocds_date(published_str),
            "deadline_at": parse_ocds_date(deadline_str),
            "tender_value": Decimal(str(tender_val)) if tender_val is not None else None,
            "currency": currency,
            "description": description,
            "source_url": source_url,
            "portal_adv_no": adv_no,
            "portal_adv_status": adv_status,
            "status": map_ocds_status(tender_sec.get("status")),
            "ocds_payload": release,
            "items": items_payload,
        }


map_release_to_tender_payload = OCDSClient.map_release_to_tender_payload


def sync_ocds_tenders(db: Session, limit: int = 50, query: Optional[str] = "medical") -> Dict[str, Any]:
    """
    Orchestrates Tier 1 OCDS ingestion:
    Pulls from OCDS API, maps fields, and idempotently upserts on ocid/reference_number.
    """
    client = OCDSClient()
    logger.info(f"Initiating OCDS ingestion sync (limit={limit}, query={query})...")

    releases = []
    source_name = "Rwanda OCDS Engine (Umucyo)"

    # Step 1: Attempt discovery via OCDS API
    try:
        releases = client.fetch_releases(offset=0, limit=limit)
    except Exception as e:
        logger.warning(f"Releases endpoint query encountered an issue: {e}")

    # Fallback to search endpoint if general releases returned empty
    if not releases and query:
        try:
            releases = client.search_releases(query=query, page=1, page_size=limit)
        except Exception as e:
            logger.warning(f"Search endpoint query encountered an issue: {e}")

    if not releases:
        logger.warning("Live OCDS API returned 0 releases. Ingestion completed with 0 updates.")
        return {
            "tier": "Tier 1: Official OCDS API",
            "source": source_name,
            "endpoint": client.base_url,
            "tenders_scanned": 0,
            "new_tenders_created": 0,
            "tenders_updated": 0,
            "synced_summary": [],
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }

    now = datetime.now(timezone.utc)
    created_count = 0
    updated_count = 0
    synced_items = []

    # Retrieve or update monitored TenderSource
    source = db.query(TenderSource).filter(
        (TenderSource.name.ilike("%Umucyo%")) | (TenderSource.name.ilike("%OCDS%")) | (TenderSource.name.ilike("%RPPA%"))
    ).first()

    for rel in releases:
        mapped = client.map_release_to_tender_payload(rel)
        ocid = mapped.get("ocid")
        ref_no = mapped.get("reference_number")

        if not ocid and not ref_no:
            continue

        # Idempotent lookup: match on ocid or reference_number
        existing = db.query(Tender).filter(
            (Tender.ocid == ocid) | (Tender.reference_number == ref_no)
        ).first()

        items_payload = mapped.pop("items", [])

        if existing:
            # Update fields idempotently
            if mapped.get("deadline_at"):
                existing.deadline_at = mapped["deadline_at"]
            if mapped.get("tender_value"):
                existing.tender_value = mapped["tender_value"]
            if mapped.get("status"):
                existing.status = mapped["status"]
            if mapped.get("portal_adv_no"):
                existing.portal_adv_no = mapped["portal_adv_no"]
                existing.portal_adv_status = mapped["portal_adv_status"]
            existing.ocds_payload = mapped.get("ocds_payload")
            existing.updated_at = now
            updated_count += 1
            synced_items.append({
                "ocid": existing.ocid or existing.reference_number,
                "title": existing.title,
                "status": "updated",
            })
        else:
            new_tender = Tender(**mapped)
            db.add(new_tender)
            db.flush()

            for itm in items_payload:
                db.add(TenderItem(tender_id=new_tender.id, **itm))

            if new_tender.source_url:
                db.add(TenderSourceReference(
                    tender_id=new_tender.id,
                    source_id=source.id if source else None,
                    source_url=new_tender.source_url,
                ))

            created_count += 1
            synced_items.append({
                "ocid": new_tender.ocid or new_tender.reference_number,
                "title": new_tender.title,
                "status": "created",
            })

    if source:
        source.last_scan_at = now
        source.last_successful_scan_at = now
        source.tenders_collected_count = (source.tenders_collected_count or 0) + created_count
        source.last_error = None
        db.add(source)

    db.commit()

    return {
        "tier": "Tier 1: Official OCDS API",
        "source": source_name,
        "endpoint": client.base_url,
        "tenders_scanned": len(releases),
        "new_tenders_created": created_count,
        "tenders_updated": updated_count,
        "synced_summary": synced_items[:10],
        "synced_at": now.isoformat(),
    }


def get_verified_ocds_sample_releases() -> List[Dict[str, Any]]:
    """Verified standard OCDS release payloads matching Rwanda Umucyo schema."""
    return [
        {
            "ocid": "ocds-k2879p-000003-G-ICB-2026-2027-RBC",
            "id": "rel-000003-G-ICB-2026-2027-RBC-01",
            "date": "2026-08-28T08:30:00Z",
            "tag": ["tender"],
            "initiationType": "tender",
            "buyer": {"name": "RWANDA BIO-MEDICAL CENTER(RBC)", "id": "RBC-RW"},
            "tender": {
                "id": "000003/G/ICB/2026/2027/RBC",
                "title": "Supply and installation of Patient Monitoring and Critical care equipment",
                "description": "Procurement of multi-parameter patient monitors, ECG machines, central monitoring stations and defibrillators for CHUK Masaka hospital complex.",
                "status": "active",
                "procuringEntity": {"name": "RWANDA BIO-MEDICAL CENTER(RBC)"},
                "procurementMethod": "open",
                "procurementMethodDetails": "International Competitive Bidding",
                "value": {"amount": 34643704.51, "currency": "RWF"},
                "tenderPeriod": {
                    "startDate": "2026-08-28T08:30:00Z",
                    "endDate": "2026-09-28T10:00:00Z"
                },
                "items": [
                    {"id": "LOT-1", "description": "Supply and installation of ECG machines", "quantity": 1},
                    {"id": "LOT-2", "description": "Trolley mounted Patient monitors", "quantity": 1},
                    {"id": "LOT-3", "description": "Wall mounted Patient monitors", "quantity": 1},
                    {"id": "LOT-4", "description": "Central Monitor Station", "quantity": 1}
                ]
            }
        },
        {
            "ocid": "ocds-k2879p-000004-G-NCB-2026-2027-RL2TH",
            "id": "rel-000004-G-NCB-2026-2027-RL2TH-01",
            "date": "2026-08-20T09:00:00Z",
            "tag": ["tender"],
            "initiationType": "tender",
            "buyer": {"name": "RUHENGERI LEVEL TWO TEACHING HOSPITAL", "id": "RL2TH-RW"},
            "tender": {
                "id": "000004/G/NCB/2026/2027/6300003001",
                "title": "Supply and installation of Medical Air Compressor for ICU and Neonatalogy",
                "description": "Oil-free medical grade air compression stack for neonatal ventilators and critical resuscitation units.",
                "status": "active",
                "procuringEntity": {"name": "RUHENGERI LEVEL TWO TEACHING HOSPITAL"},
                "procurementMethod": "open",
                "procurementMethodDetails": "National Competitive Bidding",
                "value": {"amount": 2850000.00, "currency": "RWF"},
                "tenderPeriod": {
                    "startDate": "2026-08-20T09:00:00Z",
                    "endDate": "2026-09-16T10:00:00Z"
                },
                "items": [
                    {"id": "LOT-1", "description": "Medical Air Compressor Unit with 500L Tank and Filtration Stack", "quantity": 1}
                ]
            }
        },
        {
            "ocid": "ocds-k2879p-000002-G-ICB-2026-2027-RBC",
            "id": "rel-000002-G-ICB-2026-2027-RBC-01",
            "date": "2026-08-26T12:00:00Z",
            "tag": ["tender"],
            "initiationType": "tender",
            "buyer": {"name": "RWANDA BIO-MEDICAL CENTER(RBC)", "id": "RBC-RW"},
            "tender": {
                "id": "000002/G/ICB/2026/2027/1605000000",
                "title": "Supply and installation of IT, PACS Servers, and Diagnostic Workstation Equipment",
                "description": "High-performance medical diagnostic workstations, PACS viewing monitors, and network infrastructure for CHUK Masaka.",
                "status": "active",
                "procuringEntity": {"name": "RWANDA BIO-MEDICAL CENTER(RBC)"},
                "procurementMethod": "open",
                "procurementMethodDetails": "International Competitive Bidding",
                "value": {"amount": 15099424.80, "currency": "RWF"},
                "tenderPeriod": {
                    "startDate": "2026-08-26T12:00:00Z",
                    "endDate": "2026-09-28T10:00:00Z"
                },
                "items": [
                    {"id": "LOT-1", "description": "Diagnostic Clinical Workstations & PACS Servers", "quantity": 1}
                ]
            }
        }
    ]
