import enum


class RoleName(str, enum.Enum):
    ADMIN = "admin"
    MANAGEMENT = "management"
    SALES = "sales"
    BIOMEDICAL_ENGINEER = "biomedical_engineer"
    PROCUREMENT = "procurement"
    FINANCE = "finance"
    VIEWER = "viewer"


class SourceCategory(str, enum.Enum):
    GOVERNMENT_PORTAL = "government_portal"
    MINISTRY = "ministry"
    HOSPITAL = "hospital"
    DISTRICT_HOSPITAL = "district_hospital"
    HEALTH_CENTRE = "health_centre"
    NGO = "ngo"
    UN_AGENCY = "un_agency"
    UNIVERSITY = "university"
    PRIVATE_INSTITUTION = "private_institution"
    OTHER = "other"


class CollectionMethod(str, enum.Enum):
    API = "api"
    RSS = "rss"
    SITEMAP = "sitemap"
    WEBPAGE = "webpage"
    PDF_LISTING = "pdf_listing"
    MANUAL_IMPORT = "manual_import"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGIN_FAILED = "login_failed"
    STATUS_CHANGE = "status_change"
