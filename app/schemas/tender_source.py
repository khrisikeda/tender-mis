import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, model_validator

from app.core.enums import SourceCategory, CollectionMethod


class TenderSourceCreate(BaseModel):
    name: str
    code: Optional[str] = None
    website: Optional[str] = None
    url: Optional[str] = None
    scraper_type: Optional[str] = None
    country: str = "Rwanda"
    organization: Optional[str] = None
    category: SourceCategory = SourceCategory.OTHER
    collection_method: CollectionMethod = CollectionMethod.WEBPAGE
    scan_frequency_hours: int = 24
    requires_manual_import: bool = False
    compliance_notes: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_website_and_url(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("website") and data.get("url"):
                data["website"] = data["url"]
            elif not data.get("url") and data.get("website"):
                data["url"] = data["website"]
        return data


class TenderSourceUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    website: Optional[str] = None
    url: Optional[str] = None
    scraper_type: Optional[str] = None
    country: str = None
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
    code: Optional[str] = None
    website: Optional[str] = None
    url: Optional[str] = None
    scraper_type: Optional[str] = None
    country: str
    organization: Optional[str] = None
    category: SourceCategory
    collection_method: CollectionMethod
    is_active: bool
    scan_frequency_hours: int
    requires_manual_import: bool
    last_scan_at: Optional[datetime] = None
    last_successful_scan_at: Optional[datetime] = None
    last_error: Optional[str] = None
    tenders_collected_count: int = 0
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
