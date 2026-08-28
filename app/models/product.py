import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_code = Column(String(120), unique=True, nullable=False, index=True)
    name = Column(String(300), nullable=False, index=True)
    category = Column(String(150), nullable=False, index=True)
    subcategory = Column(String(150), nullable=True)
    manufacturer = Column(String(250), nullable=False, index=True)
    brand = Column(String(150), nullable=True)
    model = Column(String(150), nullable=True)
    keywords = Column(JSON, nullable=False, default=list)
    technical_specifications = Column(JSON, nullable=False, default=dict)
    certifications = Column(JSON, nullable=False, default=list)
    supplier = Column(String(250), nullable=True)
    country_of_origin = Column(String(120), nullable=True)
    price_range = Column(Numeric(18, 2), nullable=True)
    currency = Column(String(10), nullable=True)
    lead_time = Column(String(100), nullable=True)
    availability = Column(String(100), nullable=True)
    warranty = Column(String(200), nullable=True)
    installation_requirements = Column(Text, nullable=True)
    training_requirements = Column(Text, nullable=True)
    service_capability = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)