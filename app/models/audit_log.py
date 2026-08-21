import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.core.enums import AuditAction


class AuditLog(Base):
    """
    Append-only record of who did what, when, to which record.
    Spec section 35: important records must not be silently deleted --
    this table is never updated or deleted from the application layer,
    only inserted into.
    """

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(Enum(AuditAction), nullable=False)

    entity_type = Column(String(100), nullable=False)  # e.g. "tender", "tender_source"
    entity_id = Column(UUID(as_uuid=True), nullable=True)

    previous_value = Column(Text, nullable=True)  # JSON-serialized snapshot
    new_value = Column(Text, nullable=True)  # JSON-serialized snapshot

    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type}:{self.entity_id}>"
