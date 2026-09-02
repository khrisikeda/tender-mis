import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.core.enums import SourceCategory, CollectionMethod


class TenderSource(Base):
    """
    A monitored source of procurement opportunities (a government portal,
    a hospital website, an NGO's tender page, etc.).

    This is the module described in spec section 3 (Tender Sources) --
    every field the discovery/collection service needs to know how, how
    often, and whether it's allowed to pull from a given source.
    """

    __tablename__ = "tender_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(200), nullable=False)
    code = Column(String(100), nullable=True, index=True)
    website = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)
    scraper_type = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, default="Rwanda")
    organization = Column(String(200), nullable=True)

    category = Column(Enum(SourceCategory), nullable=False, default=SourceCategory.OTHER)
    collection_method = Column(Enum(CollectionMethod), nullable=False, default=CollectionMethod.WEBPAGE)

    is_active = Column(Boolean, default=True, nullable=False)
    scan_frequency_hours = Column(Integer, default=24, nullable=False)

    # Compliance fields -- checked by the collection service before every scan.
    robots_txt_checked_at = Column(DateTime, nullable=True)
    robots_txt_allows_collection = Column(Boolean, nullable=True)
    requires_manual_import = Column(Boolean, default=False, nullable=False)
    compliance_notes = Column(Text, nullable=True)

    # Health/monitoring fields.
    last_scan_at = Column(DateTime, nullable=True)
    last_successful_scan_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    tenders_collected_count = Column(Integer, default=0, nullable=False)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TenderSource {self.name} ({self.collection_method})>"
