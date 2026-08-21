import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import EvidenceStatus, TenderStatus


class TenderItemCreate(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    specifications: Optional[dict[str, Any]] = None
    evidence_status: EvidenceStatus = EvidenceStatus.REQUIRES_HUMAN_VERIFICATION


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
    reference_number: Optional[str]
    title: str
    procuring_entity: Optional[str]
    country: str
    location: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    published_at: Optional[datetime]
    deadline_at: Optional[datetime]
    opening_at: Optional[datetime]
    timezone: str
    procurement_method: Optional[str]
    tender_value: Optional[Decimal]
    currency: Optional[str]
    description: Optional[str]
    source_url: Optional[str]
    tender_document_url: Optional[str]
    status: TenderStatus
    relevance_score: Optional[int]
    classification_status: Optional[str]
    classification_confidence: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    items: list[TenderItemOut] = Field(default_factory=list)