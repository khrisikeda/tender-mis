"""
Import every model here so that Base.metadata is complete when
Alembic (or Base.metadata.create_all) inspects it.
"""
from app.models.user import User, Role  # noqa: F401
from app.models.tender_source import TenderSource  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.tender import Tender, TenderSourceReference, TenderDocument, TenderEvidence, TenderItem  # noqa: F401
from app.models.product import Product  # noqa: F401
