import json
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.core.enums import AuditAction


def write_audit_log(
    db: Session,
    *,
    user_id: Optional[uuid.UUID],
    action: AuditAction,
    entity_type: str,
    entity_id: Optional[uuid.UUID] = None,
    previous_value: Optional[dict] = None,
    new_value: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        previous_value=json.dumps(previous_value, default=str) if previous_value else None,
        new_value=json.dumps(new_value, default=str) if new_value else None,
        ip_address=ip_address,
    )
    db.add(entry)
    # Deliberately not committing here -- caller commits as part of its own
    # transaction so the audit entry and the change it describes are atomic.
