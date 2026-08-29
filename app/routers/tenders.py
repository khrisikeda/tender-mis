import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.audit import write_audit_log
from app.core.deps import get_current_user, require_roles
from app.core.enums import AuditAction, RoleName
from app.models.tender import Tender, TenderItem, TenderSourceReference
from app.models.user import User
from app.schemas.tender import TenderCreate, TenderOut, TenderStatusUpdate

router = APIRouter(prefix="/tenders", tags=["tenders"])
MANAGE_TENDERS = require_roles([
    RoleName.ADMIN,
    RoleName.MANAGEMENT,
    RoleName.SALES,
    RoleName.PROCUREMENT,
    RoleName.BIOMEDICAL_ENGINEER,
])


@router.get("", response_model=list[TenderOut])
def list_tenders(
    status_filter: str | None = Query(default=None, alias="status"),
    country: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Tender)
    if status_filter:
        query = query.filter(Tender.status == status_filter)
    if country:
        query = query.filter(Tender.country.ilike(country))
    if category:
        query = query.filter(Tender.category.ilike(category))
    return query.order_by(Tender.deadline_at.asc().nullslast(), Tender.created_at.desc()).all()


@router.get("/{tender_id}", response_model=TenderOut)
def get_tender(
    tender_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")
    return tender


@router.post("", response_model=TenderOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(MANAGE_TENDERS)])
def create_tender(
    payload: TenderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tender = Tender(**payload.model_dump(exclude={"items"}))
    db.add(tender)
    db.flush()

    for item_payload in payload.items:
        db.add(TenderItem(tender_id=tender.id, **item_payload.model_dump()))

    if payload.source_url:
        db.add(TenderSourceReference(tender_id=tender.id, source_url=payload.source_url))

    write_audit_log(
        db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="tender",
        entity_id=tender.id,
        new_value=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(tender)
    return tender


@router.post("/{tender_id}/status", response_model=TenderOut, dependencies=[Depends(MANAGE_TENDERS)])
def update_tender_status(
    tender_id: uuid.UUID,
    payload: TenderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")

    previous_status = tender.status.value
    tender.status = payload.status
    if payload.notes is not None:
        tender.notes = payload.notes
    write_audit_log(
        db,
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGE,
        entity_type="tender",
        entity_id=tender.id,
        previous_value={"status": previous_status},
        new_value=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(tender)
    return tender


@router.post("/extract-document")
async def extract_tender_document(
    file: UploadFile = File(...),
):
    """
    Extracts specifications, reference number, buyer entity, deadline, and line items
    from an uploaded Word (.docx / .doc) or PDF bidding document.
    """
    from app.services.document_extractor import TenderDocumentExtractor

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    extracted = TenderDocumentExtractor.extract_from_file(file_bytes, file.filename)
    return extracted