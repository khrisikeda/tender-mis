import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.audit import write_audit_log
from app.core.enums import AuditAction, RoleName
from app.models.user import User
from app.models.tender_source import TenderSource
from app.schemas.tender_source import TenderSourceCreate, TenderSourceUpdate, TenderSourceOut

router = APIRouter(prefix="/tender-sources", tags=["tender-sources"])

# Managing sources is an Admin/Management responsibility; everyone else can
# read the list (e.g. to understand coverage) but not change it.
MANAGE_SOURCES = require_roles([RoleName.ADMIN, RoleName.MANAGEMENT])


@router.get("", response_model=list[TenderSourceOut])
def list_sources(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(TenderSource)
    if is_active is not None:
        query = query.filter(TenderSource.is_active == is_active)
    return query.order_by(TenderSource.name).all()


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


@router.post("", response_model=TenderSourceOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(MANAGE_SOURCES)])
def create_source(
    payload: TenderSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source = TenderSource(**payload.model_dump())
    db.add(source)
    db.flush()

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


@router.post("/{source_id}/scan", dependencies=[Depends(MANAGE_SOURCES)])
async def scan_source(
    source_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Executes an on-demand extraction scan for a specific monitored tender source.
    """
    source = db.query(TenderSource).filter(TenderSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender source not found")

    from app.services.umucyo_crawler import sync_umucyo_tenders
    result = await sync_umucyo_tenders(db=db)

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


@router.post("/sync/umucyo", dependencies=[Depends(MANAGE_SOURCES)])
async def sync_umucyo_direct(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Directly initiates a live crawler pass across Rwanda's Umucyo e-Procurement portal.
    """
    from app.services.umucyo_crawler import sync_umucyo_tenders
    result = await sync_umucyo_tenders(db=db)

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

