import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import EvidenceStatus, TenderStatus


class TenderItemCreate(BaseModel):
    description: Optional[str] = None
    title: Optional[str] = None
    lot_number: Optional[int] = None
    item_number: Optional[int] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    specifications: Optional[dict[str, Any]] = None
    specifications_raw: Optional[str] = None
    evidence_status: EvidenceStatus = EvidenceStatus.REQUIRES_HUMAN_VERIFICATION

    @model_validator(mode="before")
    @classmethod
    def sync_description_and_title(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("description") and data.get("title"):
                data["description"] = data["title"]
            elif not data.get("title") and data.get("description"):
                data["title"] = data["description"]
        return data


class TenderCreate(BaseModel):
    reference_number: Optional[str] = None
    title: str = Field(min_length=1, max_length=500)
    procuring_entity: Optional[str] = None
    country: str = "Rwanda"
    location: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    published_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None
    opening_at: Optional[datetime] = None
    timezone: str = "Africa/Kigali"
    procurement_method: Optional[str] = None
    tender_value: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    tender_document_url: Optional[str] = None
    # OCDS & Portal Identification
    ocid: Optional[str] = None
    ocds_release_id: Optional[str] = None
    ocds_payload: Optional[dict[str, Any]] = None
    portal_adv_no: Optional[str] = None
    portal_adv_status: Optional[str] = None

    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    notes: Optional[str] = None
    items: list[TenderItemCreate] = Field(default_factory=list)


class TenderStatusUpdate(BaseModel):
    status: TenderStatus
    notes: Optional[str] = None


class TenderItemOut(TenderItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class TenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference_number: Optional[str] = None
    title: str
    procuring_entity: Optional[str] = None
    country: str = "Rwanda"
    location: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    published_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None
    opening_at: Optional[datetime] = None
    timezone: str = "Africa/Kigali"
    procurement_method: Optional[str] = None
    tender_value: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    tender_document_url: Optional[str] = None
    # OCDS & Portal Identification
    ocid: Optional[str] = None
    ocds_release_id: Optional[str] = None
    ocds_payload: Optional[dict[str, Any]] = None
    portal_adv_no: Optional[str] = None
    portal_adv_status: Optional[str] = None

    status: TenderStatus
    relevance_score: Optional[int] = None
    classification_status: Optional[str] = None
    classification_confidence: Optional[Decimal] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: list[TenderItemOut] = Field(default_factory=list)