import math
import uuid
from typing import Any, Optional, Union

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.audit import write_audit_log
from app.core.deps import get_current_user, get_current_user_optional, require_roles
from app.core.enums import AuditAction, RoleName, TenderStatus
from app.models.tender import Tender, TenderItem, TenderSourceReference
from app.models.user import User
from app.schemas.tender import (
    DocumentLinkOut,
    EstimatedValueOut,
    NormalizedTenderOut,
    PaginatedTendersOut,
    TenderCreate,
    TenderOut,
    TenderStatusUpdate,
)

router = APIRouter(prefix="/tenders", tags=["tenders"])
MANAGE_TENDERS = require_roles([
    RoleName.ADMIN,
    RoleName.MANAGEMENT,
    RoleName.SALES,
    RoleName.PROCUREMENT,
    RoleName.BIOMEDICAL_ENGINEER,
])


def normalize_tender(t: Tender) -> NormalizedTenderOut:
    """Transforms database Tender record into the normalized OCDS schema."""
    status_label_map = {
        TenderStatus.NEW: "Active",
        TenderStatus.REVIEW: "Under Review",
        TenderStatus.INTERESTED: "Interested",
        TenderStatus.QUALIFICATION_CHECK: "Qualification Check",
        TenderStatus.BID_PREPARATION: "Bid Preparation",
        TenderStatus.SUBMITTED: "Submitted",
        TenderStatus.AWARDED: "Awarded",
        TenderStatus.LOST: "Closed",
        TenderStatus.CANCELLED: "Cancelled",
        TenderStatus.NOT_ELIGIBLE: "Not Eligible",
    }
    status_val = t.status.value if hasattr(t.status, "value") else str(t.status)
    clean_status = status_label_map.get(t.status, status_val.title().replace("_", " "))

    val_amt = float(t.tender_value) if t.tender_value is not None else None
    val_currency = t.currency or "RWF"
    formatted_val = f"{val_amt:,.2f} {val_currency}" if val_amt is not None else "Not Disclosed"

    est_val = EstimatedValueOut(
        amount=val_amt,
        currency=val_currency,
        formatted=formatted_val,
    )

    docs = []
    if t.source_url:
        docs.append(DocumentLinkOut(
            title="Umucyo Official Notice",
            url=t.source_url,
            document_type="portal_notice",
        ))
    if t.tender_document_url:
        docs.append(DocumentLinkOut(
            title="Tender Bidding Document",
            url=t.tender_document_url,
            document_type="bidding_document",
        ))

    items_list = []
    for itm in t.items:
        items_list.append({
            "id": str(itm.id),
            "lot_number": itm.lot_number,
            "item_number": itm.item_number,
            "title": itm.title or itm.description,
            "description": itm.description,
            "quantity": float(itm.quantity) if itm.quantity is not None else 1.0,
            "unit": itm.unit,
            "specifications": itm.specifications,
        })

    pub_date = t.published_at.isoformat() if t.published_at else None
    sub_deadline = t.deadline_at.isoformat() if t.deadline_at else None
    tender_no = t.reference_number or t.portal_adv_no or str(t.id)[:8]

    return NormalizedTenderOut(
        id=t.ocid or str(t.id),
        tenderNo=tender_no,
        title=t.title,
        description=t.description or t.title,
        procuringEntity=t.procuring_entity or "Rwanda Public Procurement Authority",
        status=clean_status,
        publicationDate=pub_date,
        submissionDeadline=sub_deadline,
        estimatedValue=est_val,
        documents=docs,
        # Backward-compatibility fields
        reference_number=t.reference_number or tender_no,
        procuring_entity=t.procuring_entity or "Rwanda Public Procurement Authority",
        published_at=pub_date,
        deadline_at=sub_deadline,
        tender_value=val_amt,
        currency=val_currency,
        category=t.category or "Medical Equipment",
        country=t.country or "Rwanda",
        source_url=t.source_url,
        tender_document_url=t.tender_document_url,
        ocid=t.ocid,
        portal_adv_no=t.portal_adv_no,
        portal_adv_status=t.portal_adv_status,
        relevance_score=t.relevance_score or 85,
        items=items_list,
    )


@router.get("", response_model=Union[PaginatedTendersOut, list[NormalizedTenderOut]])
def list_tenders(
    response: Response,
    q: Optional[str] = Query(default=None, description="Search query across title, procuringEntity, and tenderNo"),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    country: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    paginated: bool = Query(default=False, description="Return wrapped object with pagination metadata"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    query = db.query(Tender)

    # Multi-field search
    if q and q.strip():
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Tender.title.ilike(search_pattern),
                Tender.procuring_entity.ilike(search_pattern),
                Tender.reference_number.ilike(search_pattern),
                Tender.portal_adv_no.ilike(search_pattern),
                Tender.description.ilike(search_pattern),
                Tender.ocid.ilike(search_pattern),
            )
        )

    # Filter status
    if status_filter and status_filter.strip():
        val = status_filter.strip().lower()
        if val in {"active", "new"}:
            query = query.filter(Tender.status == TenderStatus.NEW)
        elif val in {"review", "under_review", "under review"}:
            query = query.filter(Tender.status == TenderStatus.REVIEW)
        elif val in {"awarded"}:
            query = query.filter(Tender.status == TenderStatus.AWARDED)
        elif val in {"closed", "lost"}:
            query = query.filter(Tender.status == TenderStatus.LOST)
        elif val in {"bid_preparation", "bid preparation"}:
            query = query.filter(Tender.status == TenderStatus.BID_PREPARATION)
        else:
            try:
                enum_status = TenderStatus(status_filter.strip())
                query = query.filter(Tender.status == enum_status)
            except ValueError:
                pass

    if country:
        query = query.filter(Tender.country.ilike(country))
    if category:
        query = query.filter(Tender.category.ilike(category))

    total_count = query.count()
    total_pages = max(1, math.ceil(total_count / page_size)) if total_count > 0 else 1

    # Order and paginate
    ordered_query = query.order_by(Tender.deadline_at.asc().nullslast(), Tender.created_at.desc())
    offset = (page - 1) * page_size
    records = ordered_query.offset(offset).limit(page_size).all()

    normalized_items = [normalize_tender(t) for t in records]

    # Expose pagination headers
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Page"] = str(page)
    response.headers["X-Page-Size"] = str(page_size)
    response.headers["X-Total-Pages"] = str(total_pages)

    if paginated:
        return PaginatedTendersOut(
            items=normalized_items,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    return normalized_items


@router.get("/{tender_id}", response_model=NormalizedTenderOut)
def get_tender(
    tender_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    tender = None
    try:
        tender_uuid = uuid.UUID(tender_id)
        tender = db.query(Tender).filter(Tender.id == tender_uuid).first()
    except (ValueError, TypeError):
        pass

    if not tender:
        tender = db.query(Tender).filter(
            or_(
                Tender.ocid == tender_id,
                Tender.reference_number == tender_id,
                Tender.portal_adv_no == tender_id,
            )
        ).first()

    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")

    return normalize_tender(tender)


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