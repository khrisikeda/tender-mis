import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    product_code: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=300)
    category: str = Field(min_length=1, max_length=150)
    subcategory: Optional[str] = None
    manufacturer: str = Field(min_length=1, max_length=250)
    brand: Optional[str] = None
    model: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    technical_specifications: dict[str, Any] = Field(default_factory=dict)
    certifications: list[str] = Field(default_factory=list)
    supplier: Optional[str] = None
    country_of_origin: Optional[str] = None
    price_range: Optional[Decimal] = None
    currency: Optional[str] = None
    lead_time: Optional[str] = None
    availability: Optional[str] = None
    warranty: Optional[str] = None
    installation_requirements: Optional[str] = None
    training_requirements: Optional[str] = None
    service_capability: Optional[str] = None


class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductMatchOut(ProductOut):
    match_score: float
    matched_terms: list[str] = Field(default_factory=list)
    match_reason: str