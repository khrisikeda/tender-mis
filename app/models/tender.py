import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.core.enums import EvidenceStatus, ExtractionStatus, TenderStatus


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_number = Column(String(200), nullable=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    procuring_entity = Column(String(300), nullable=True, index=True)
    country = Column(String(100), nullable=False, default="Rwanda", index=True)
    location = Column(String(300), nullable=True)
    category = Column(String(150), nullable=True, index=True)
    subcategory = Column(String(150), nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    deadline_at = Column(DateTime, nullable=True, index=True)
    opening_at = Column(DateTime, nullable=True)
    timezone = Column(String(64), nullable=False, default="Africa/Kigali")
    procurement_method = Column(String(150), nullable=True)
    tender_value = Column(Numeric(18, 2), nullable=True)
    currency = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    source_url = Column(String(1000), nullable=True)
    tender_document_url = Column(String(1000), nullable=True)
    contact_name = Column(String(200), nullable=True)
    contact_email = Column(String(320), nullable=True)
    contact_telephone = Column(String(80), nullable=True)
    status = Column(Enum(TenderStatus), nullable=False, default=TenderStatus.NEW, index=True)
    relevance_score = Column(Integer, nullable=True)
    classification_status = Column(String(40), nullable=True)
    classification_confidence = Column(Numeric(5, 2), nullable=True)
    notes = Column(Text, nullable=True)
    is_duplicate = Column(Boolean, nullable=False, default=False)
    duplicate_of_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("TenderItem", back_populates="tender", cascade="all, delete-orphan")


class TenderSourceReference(Base):
    __tablename__ = "tender_source_references"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("tender_sources.id"), nullable=True, index=True)
    source_url = Column(String(1000), nullable=False)
    first_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    content_hash = Column(String(128), nullable=True, index=True)


class TenderDocument(Base):
    __tablename__ = "tender_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False, index=True)
    filename = Column(String(300), nullable=False)
    document_url = Column(String(1000), nullable=True)
    storage_key = Column(String(1000), nullable=True)
    mime_type = Column(String(100), nullable=True)
    document_hash = Column(String(128), nullable=True, index=True)
    extraction_status = Column(Enum(ExtractionStatus), nullable=False, default=ExtractionStatus.PENDING)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TenderEvidence(Base):
    __tablename__ = "tender_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("tender_documents.id"), nullable=True)
    field_name = Column(String(100), nullable=False, index=True)
    field_value = Column(JSON, nullable=True)
    evidence_status = Column(Enum(EvidenceStatus), nullable=False)
    page_number = Column(Integer, nullable=True)
    section = Column(String(300), nullable=True)
    quote = Column(Text, nullable=True)
    confidence = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TenderItem(Base):
    __tablename__ = "tender_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("tenders.id"), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(18, 3), nullable=True)
    unit = Column(String(80), nullable=True)
    specifications = Column(JSON, nullable=True)
    evidence_status = Column(Enum(EvidenceStatus), nullable=False, default=EvidenceStatus.REQUIRES_HUMAN_VERIFICATION)

    tender = relationship("Tender", back_populates="items")