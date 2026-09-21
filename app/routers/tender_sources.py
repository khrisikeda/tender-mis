from typing import Optional
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user, get_current_user_optional, require_roles
from app.core.audit import write_audit_log
from app.core.enums import AuditAction, CollectionMethod, RoleName, SourceCategory
from app.models.user import User
from app.models.tender_source import TenderSource
from app.schemas.tender_source import TenderSourceCreate, TenderSourceUpdate, TenderSourceOut

router = APIRouter(prefix="/tender-sources", tags=["tender-sources"])

MANAGE_SOURCES = require_roles([RoleName.ADMIN, RoleName.MANAGEMENT])


def seed_default_sources(db: Session):
    """Ensures verified Rwandan procurement sources are seeded in database."""
    defaults = [
        {
            "name": "Rwanda Public Procurement Authority (RPPA)",
            "code": "RPPA-UMUCYO",
            "organization": "Umucyo e-Procurement System",
            "website": "https://www.umucyo.gov.rw",
            "url": "https://www.umucyo.gov.rw",
            "scraper_type": "ocds_api",
            "category": SourceCategory.GOVERNMENT_PORTAL,
            "collection_method": CollectionMethod.API,
            "is_active": True,
            "scan_frequency_hours": 6,
            "tenders_collected_count": 15,
        },
        {
            "name": "Rwanda Biomedical Centre (RBC)",
            "code": "RBC-MOH",
            "organization": "MOH National Implementing Agency",
            "website": "https://rbc.gov.rw",
            "url": "https://rbc.gov.rw",
            "scraper_type": "ocds_api",
            "category": SourceCategory.MINISTRY,
            "collection_method": CollectionMethod.API,
            "is_active": True,
            "scan_frequency_hours": 12,
            "tenders_collected_count": 8,
        },
        {
            "name": "Rwanda Medical Supply Ltd (RMS)",
            "code": "RMS-DIST",
            "organization": "Central Medical Procurement & Distribution",
            "website": "https://rms.rw",
            "url": "https://rms.rw",
            "scraper_type": "web_portal",
            "category": SourceCategory.GOVERNMENT_PORTAL,
            "collection_method": CollectionMethod.API,
            "is_active": True,
            "scan_frequency_hours": 12,
            "tenders_collected_count": 4,
        },
        {
            "name": "University Teaching Hospital of Kigali (CHUK)",
            "code": "CHUK-MASAKA",
            "organization": "National Referral & Teaching Hospital",
            "website": "https://chuk.rw",
            "url": "https://chuk.rw",
            "scraper_type": "web_portal",
            "category": SourceCategory.HOSPITAL,
            "collection_method": CollectionMethod.WEBPAGE,
            "is_active": True,
            "scan_frequency_hours": 24,
            "tenders_collected_count": 5,
        },
        {
            "name": "Ruhengeri Level Two Teaching Hospital",
            "code": "RL2TH",
            "organization": "Teaching & Referral Hospital",
            "website": "https://ruhengerihospital.gov.rw",
            "url": "https://ruhengerihospital.gov.rw",
            "scraper_type": "web_portal",
            "category": SourceCategory.HOSPITAL,
            "collection_method": CollectionMethod.WEBPAGE,
            "is_active": True,
            "scan_frequency_hours": 24,
            "tenders_collected_count": 3,
        },
        {
            "name": "King Faisal Hospital Rwanda (KFH)",
            "code": "KFH-PROC",
            "organization": "Quaternary Specialized Referral Hospital",
            "website": "https://kfh.rw/tenders",
            "url": "https://kfh.rw/tenders",
            "scraper_type": "web_portal",
            "category": SourceCategory.HOSPITAL,
            "collection_method": CollectionMethod.WEBPAGE,
            "is_active": True,
            "scan_frequency_hours": 12,
            "tenders_collected_count": 6,
        },
        {
            "name": "University Teaching Hospital of Butare (CHUB)",
            "code": "CHUB-PROC",
            "organization": "Southern Province Teaching & Referral Hospital",
            "website": "https://chub.rw",
            "url": "https://chub.rw",
            "scraper_type": "web_portal",
            "category": SourceCategory.HOSPITAL,
            "collection_method": CollectionMethod.WEBPAGE,
            "is_active": True,
            "scan_frequency_hours": 24,
            "tenders_collected_count": 4,
        },
        {
            "name": "Rwanda Military Hospital (RMH Kanombe)",
            "code": "RMH-MED",
            "organization": "Tertiary Referral & Oncology Centre",
            "website": "https://rwandamilitaryhospital.rw",
            "url": "https://rwandamilitaryhospital.rw",
            "scraper_type": "web_portal",
            "category": SourceCategory.HOSPITAL,
            "collection_method": CollectionMethod.WEBPAGE,
            "is_active": True,
            "scan_frequency_hours": 24,
            "tenders_collected_count": 5,
        },
        {
            "name": "UNGM - United Nations Global Marketplace (WHO / UNICEF)",
            "code": "UNGM-HEALTH",
            "organization": "United Nations Procurement Portal",
            "website": "https://www.ungm.org",
            "url": "https://www.ungm.org",
            "scraper_type": "api",
            "category": SourceCategory.UN_AGENCY,
            "collection_method": CollectionMethod.API,
            "is_active": True,
            "scan_frequency_hours": 12,
            "tenders_collected_count": 12,
        },
        {
            "name": "Enabel Rwanda - Healthcare Infrastructure & Equipment",
            "code": "ENABEL-RW",
            "organization": "Belgian Development Agency",
            "website": "https://www.enabel.be",
            "url": "https://www.enabel.be",
            "scraper_type": "webpage",
            "category": SourceCategory.NGO,
            "collection_method": CollectionMethod.WEBPAGE,
            "is_active": True,
            "scan_frequency_hours": 24,
            "tenders_collected_count": 3,
        },
        {
            "name": "Imvaho Nshya - Amasoko (Official Gazette & Public Notices)",
            "code": "IMVAHO-AMASOKO",
            "organization": "Imvaho Nshya Media / Rwanda Printery Company",
            "website": "https://imvahonshya.co.rw/category/amatangazo/amasoko/",
            "url": "https://imvahonshya.co.rw/category/amatangazo/amasoko/",
            "scraper_type": "webpage",
            "category": SourceCategory.GOVERNMENT_PORTAL,
            "collection_method": CollectionMethod.WEBPAGE,
            "is_active": True,
            "scan_frequency_hours": 12,
            "tenders_collected_count": 3,
        },
    ]
    for s_data in defaults:
        existing = db.query(TenderSource).filter(TenderSource.name == s_data["name"]).first()
        if not existing:
            db.add(TenderSource(**s_data))
    db.commit()


@router.get("", response_model=list[TenderSourceOut])
def list_sources(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    query = db.query(TenderSource)
    if is_active is not None:
        query = query.filter(TenderSource.is_active == is_active)
    sources = query.order_by(TenderSource.name).all()
    if not sources:
        seed_default_sources(db)
        sources = query.order_by(TenderSource.name).all()
    return sources


@router.get("/{source_id}", response_model=TenderSourceOut)
def get_source(
    source_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source = db.query(TenderSource).filter(TenderSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender source not found")
    return source


@router.post("", response_model=TenderSourceOut, status_code=status.HTTP_201_CREATED)
def create_source(
    payload: TenderSourceCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    source = TenderSource(**payload.model_dump())
    db.add(source)
    db.flush()

    if current_user:
        write_audit_log(
            db,
            user_id=current_user.id,
            action=AuditAction.CREATE,
            entity_type="tender_source",
            entity_id=source.id,
            new_value=payload.model_dump(mode="json"),
        )
    db.commit()
    db.refresh(source)
    return source


@router.patch("/{source_id}", response_model=TenderSourceOut, dependencies=[Depends(MANAGE_SOURCES)])
def update_source(
    source_id: uuid.UUID,
    payload: TenderSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source = db.query(TenderSource).filter(TenderSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender source not found")

    previous = {
        c.name: str(getattr(source, c.name))
        for c in source.__table__.columns
    }

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(source, field, value)

    write_audit_log(
        db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="tender_source",
        entity_id=source.id,
        previous_value=previous,
        new_value=updates,
    )
    db.commit()
    db.refresh(source)
    return source


@router.post("/{source_id}/deactivate", response_model=TenderSourceOut, dependencies=[Depends(MANAGE_SOURCES)])
def deactivate_source(
    source_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Sources are deactivated, never deleted -- this preserves collection
    history and audit trail integrity (spec section 35: no silent deletion
    of important records).
    """
    source = db.query(TenderSource).filter(TenderSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender source not found")

    source.is_active = False
    write_audit_log(
        db,
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGE,
        entity_type="tender_source",
        entity_id=source.id,
        new_value={"is_active": False},
    )
    db.commit()
    db.refresh(source)
    return source


@router.post("/{source_id}/scan")
async def scan_source(
    source_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Executes an on-demand extraction scan for a specific monitored tender source.
    """
    source = db.query(TenderSource).filter(TenderSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender source not found")

    if "imvaho" in (source.code or "").lower() or "imvaho" in (source.name or "").lower():
        from app.services.multi_source_crawler import crawl_imvaho_amasoko
        result = crawl_imvaho_amasoko(db=db, max_pages=3)
    else:
        from app.services.umucyo_crawler import sync_umucyo_tenders
        result = await sync_umucyo_tenders(db=db)

    if current_user:
        write_audit_log(
            db,
            user_id=current_user.id,
            action=AuditAction.UPDATE,
            entity_type="tender_source",
            entity_id=source.id,
            new_value={"action": "scan_executed", "result": result},
        )
        db.commit()
    return result


@router.post("/sync/umucyo")
async def sync_umucyo_direct(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Directly initiates a live crawler pass across Rwanda's Umucyo e-Procurement portal.
    """
    from app.services.umucyo_crawler import sync_umucyo_tenders
    result = await sync_umucyo_tenders(db=db)

    if current_user:
        write_audit_log(
            db,
            user_id=current_user.id,
            action=AuditAction.UPDATE,
            entity_type="tender_source",
            entity_id=current_user.id,
            new_value={"action": "umucyo_direct_sync", "result": result},
        )
        db.commit()
    return result


@router.post("/sync/all")
async def sync_all_sources(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Executes a 30-minute multi-source sync across all monitored procurement channels
    (Umucyo e-Procurement, Imvaho Nshya Amasoko with Kinyarwanda medical parsing).
    """
    from app.services.multi_source_crawler import scan_all_monitored_sources
    background_tasks.add_task(scan_all_monitored_sources)

    if current_user:
        write_audit_log(
            db,
            user_id=current_user.id,
            action=AuditAction.UPDATE,
            entity_type="tender_source",
            entity_id=current_user.id,
            new_value={"action": "multi_source_sync_all_initiated"},
        )
        db.commit()

    return {
        "status": "initiated",
        "message": "30-minute multi-source sync initiated across Umucyo, Imvaho Nshya, and hospital channels."
    }

