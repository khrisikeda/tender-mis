import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.core.enums import SourceCategory, CollectionMethod


class TenderSourceCreate(BaseModel):
    name: str
    website: str
    country: str = "Rwanda"
    organization: Optional[str] = None
    category: SourceCategory = SourceCategory.OTHER
    collection_method: CollectionMethod
    scan_frequency_hours: int = 24
    requires_manual_import: bool = False
    compliance_notes: Optional[str] = None
    notes: Optional[str] = None


class TenderSourceUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    organization: Optional[str] = None
    category: Optional[SourceCategory] = None
    collection_method: Optional[CollectionMethod] = None
    is_active: Optional[bool] = None
    scan_frequency_hours: Optional[int] = None
    requires_manual_import: Optional[bool] = None
    compliance_notes: Optional[str] = None
    notes: Optional[str] = None


class TenderSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    website: str
    country: str
    organization: Optional[str]
    category: SourceCategory
    collection_method: CollectionMethod
    is_active: bool
    scan_frequency_hours: int
    requires_manual_import: bool
    last_scan_at: Optional[datetime]
    last_successful_scan_at: Optional[datetime]
    last_error: Optional[str]
    tenders_collected_count: int
    created_at: datetime
    updated_at: Optional[datetime]
