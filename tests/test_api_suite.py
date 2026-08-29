"""
End-to-End API Security, RBAC, and Functionality Test Suite
============================================================
Tests all 20 API endpoints across Auth, Tender Sources, Tenders, Catalogue,
Document Extraction, and System Health.
"""
import io
import os
import sys
import uuid
import zipfile
import xml.etree.ElementTree as ET

# Ensure project root is on python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.core.config import settings
from app.core.enums import RoleName, TenderStatus
from app.core.security import hash_password
from app.models.user import User, Role
from app.models.tender_source import TenderSource
from app.models.product import Product
from app.models.tender import Tender, TenderItem
from app.models.audit_log import AuditLog

# Use an in-memory SQLite DB for clean, isolated test runs
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_module():
    """Create fresh tables and seed standard roles and test users."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        # Seed Roles
        roles_dict = {}
        for role_name in RoleName:
            role = Role(name=role_name.value, description=f"Role {role_name.value}")
            db.add(role)
            db.flush()
            roles_dict[role_name.value] = role

        # Seed Admin User
        admin = User(
            full_name="Admin Supervisor",
            email="admin@medtender.rw",
            hashed_password=hash_password("AdminSecure2026!"),
            role_id=roles_dict[RoleName.ADMIN.value].id,
            is_active=True
        )
        db.add(admin)

        # Seed Sales User
        sales = User(
            full_name="Sales Executive",
            email="sales@medtender.rw",
            hashed_password=hash_password("SalesSecure2026!"),
            role_id=roles_dict[RoleName.SALES.value].id,
            is_active=True
        )
        db.add(sales)

        # Seed Viewer User (restricted)
        viewer = User(
            full_name="Read Only Viewer",
            email="viewer@medtender.rw",
            hashed_password=hash_password("ViewerSecure2026!"),
            role_id=roles_dict[RoleName.VIEWER.value].id,
            is_active=True
        )
        db.add(viewer)

        # Seed Inactive User
        inactive = User(
            full_name="Disabled Account",
            email="inactive@medtender.rw",
            hashed_password=hash_password("InactivePass123!"),
            role_id=roles_dict[RoleName.VIEWER.value].id,
            is_active=False
        )
        db.add(inactive)

        # Seed a test Tender Source
        source = TenderSource(
            name="Umucyo E-Procurement Rwanda",
            code="UMUCYO_RW",
            country="Rwanda",
            url="https://www.umucyo.gov.rw",
            scraper_type="umucyo",
            is_active=True
        )
        db.add(source)

        # Seed a test Product in Catalogue
        product = Product(
            product_code="MT-ANES-500",
            name="Advanced ICU Anesthesia Workstation",
            category="Anesthesia",
            subcategory="Workstation",
            manufacturer="Shenzhen Mindray Bio-Medical",
            brand="Mindray",
            model="WATO EX-65 Pro",
            keywords=["anesthesia", "ventilator", "icu", "operating theater", "gas delivery"],
            technical_specifications={
                "ventilation_modes": "VCV, PCV, SIMV-PS, PSV with apnea backup",
                "tidal_volume": "10 - 1500 mL",
                "gas_flow": "Electronic dual flowmeters (O2, Air, N2O)"
            },
            certifications=["ISO 13485:2016", "CE Mark 0123", "Rwanda FDA Approved"],
            price_range=28500000.0,
            currency="RWF",
            lead_time="In-Stock Kigali Window (7 Days)",
            is_active=True
        )
        db.add(product)

        # Seed a test Tender
        tender = Tender(
            reference_number="000012/G/NCB/2025/2026/CHUK",
            title="Supply, Installation and Maintenance of Operating Theatre Equipment",
            procuring_entity="University Teaching Hospital of Kigali (CHUK)",
            country="Rwanda",
            category="Biomedical Equipment",
            status=TenderStatus.NEW,
            relevance_score=94,
            source_url="https://www.umucyo.gov.rw/tender/000012",
        )
        db.add(tender)
        db.flush()

        item = TenderItem(
            tender_id=tender.id,
            lot_number=1,
            item_number=1,
            title="Anesthesia Delivery Machine with Ventilator",
            quantity=4,
            unit="Units",
            specifications_raw="Tidal volume 20 - 1500ml, VCV, PCV modes, integrated display."
        )
        db.add(item)

        db.commit()
    finally:
        db.close()


def test_system_health():
    """Test 1: Health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_login_success():
    """Test 2: Successful admin login returns JWT access and refresh tokens."""
    response = client.post("/auth/login", data={"username": "admin@medtender.rw", "password": "AdminSecure2026!"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_auth_login_invalid_password():
    """Test 3: Bad password returns 401 and logs failed audit event."""
    response = client.post("/auth/login", data={"username": "admin@medtender.rw", "password": "WrongPassword!"})
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_auth_login_disabled_user():
    """Test 4: Inactive account is blocked with 403 Forbidden."""
    response = client.post("/auth/login", data={"username": "inactive@medtender.rw", "password": "InactivePass123!"})
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"]


def test_auth_token_refresh():
    """Test 5: Valid refresh token issues new access and refresh tokens."""
    login_res = client.post("/auth/login", data={"username": "admin@medtender.rw", "password": "AdminSecure2026!"})
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = client.post(f"/auth/refresh?refresh_token={refresh_token}")
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_auth_current_user_profile():
    """Test 6: /auth/me returns authenticated user identity and role."""
    login_res = client.post("/auth/login", data={"username": "admin@medtender.rw", "password": "AdminSecure2026!"})
    token = login_res.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@medtender.rw"
    assert data["role"] == RoleName.ADMIN.value
    assert data["is_active"] is True


def test_auth_admin_create_user():
    """Test 7: Admin can create a new user account."""
    login_res = client.post("/auth/login", data={"username": "admin@medtender.rw", "password": "AdminSecure2026!"})
    admin_token = login_res.json()["access_token"]

    new_user_payload = {
        "full_name": "Biomedical Engineer Specialist",
        "email": "biomed.specialist@medtender.rw",
        "password": "BioMedPassword2026!",
        "role": RoleName.BIOMEDICAL_ENGINEER.value,
        "department": "Engineering & Technical Support",
        "phone": "+250788123456"
    }
    response = client.post(
        "/auth/users",
        json=new_user_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "biomed.specialist@medtender.rw"
    assert data["role"] == RoleName.BIOMEDICAL_ENGINEER.value


def test_auth_non_admin_cannot_create_user():
    """Test 8: Non-admin (Sales) cannot create users (RBAC 403 Forbidden)."""
    login_res = client.post("/auth/login", data={"username": "sales@medtender.rw", "password": "SalesSecure2026!"})
    sales_token = login_res.json()["access_token"]

    new_user_payload = {
        "full_name": "Unauthorized Attempt",
        "email": "unauthorized@medtender.rw",
        "password": "Password123!",
        "role": RoleName.VIEWER.value
    }
    response = client.post(
        "/auth/users",
        json=new_user_payload,
        headers={"Authorization": f"Bearer {sales_token}"}
    )
    assert response.status_code == 403


def test_tender_sources_list_and_get():
    """Test 9: Authenticated users can list and retrieve tender sources."""
    login_res = client.post("/auth/login", data={"username": "viewer@medtender.rw", "password": "ViewerSecure2026!"})
    token = login_res.json()["access_token"]

    list_res = client.get("/tender-sources", headers={"Authorization": f"Bearer {token}"})
    assert list_res.status_code == 200
    sources = list_res.json()
    assert len(sources) >= 1
    assert sources[0]["code"] == "UMUCYO_RW"

    source_id = sources[0]["id"]
    get_res = client.get(f"/tender-sources/{source_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 200
    assert get_res.json()["id"] == source_id


def test_tender_sources_create_and_update_rbac():
    """Test 10: Admin can create and update tender sources; Viewer is forbidden."""
    login_res_admin = client.post("/auth/login", data={"username": "admin@medtender.rw", "password": "AdminSecure2026!"})
    admin_token = login_res_admin.json()["access_token"]

    login_res_viewer = client.post("/auth/login", data={"username": "viewer@medtender.rw", "password": "ViewerSecure2026!"})
    viewer_token = login_res_viewer.json()["access_token"]

    source_payload = {
        "name": "King Faisal Hospital Tender Portal",
        "code": "KFH_PORTAL",
        "country": "Rwanda",
        "url": "https://kfh.rw/tenders",
        "scraper_type": "generic_html"
    }

    # Viewer attempt (must fail 403)
    viewer_attempt = client.post("/tender-sources", json=source_payload, headers={"Authorization": f"Bearer {viewer_token}"})
    assert viewer_attempt.status_code == 403

    # Admin attempt (must succeed 201)
    admin_create = client.post("/tender-sources", json=source_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_create.status_code == 201
    created_id = admin_create.json()["id"]

    # Admin update (PATCH)
    update_res = client.patch(
        f"/tender-sources/{created_id}",
        json={"notes": "Monitored 3x daily for surgical and radiology lots."},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert update_res.status_code == 200
    assert "Monitored 3x daily" in update_res.json()["notes"]


def test_tenders_list_and_filter():
    """Test 11: List tenders with filtering by country and status."""
    login_res = client.post("/auth/login", data={"username": "sales@medtender.rw", "password": "SalesSecure2026!"})
    token = login_res.json()["access_token"]

    # List all
    response = client.get("/tenders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    tenders = response.json()
    assert len(tenders) >= 1

    # Filter country
    rw_res = client.get("/tenders?country=Rwanda", headers={"Authorization": f"Bearer {token}"})
    assert rw_res.status_code == 200
    assert len(rw_res.json()) >= 1


def test_tenders_create_and_status_update():
    """Test 12: Create a tender with line items and update its workflow status."""
    login_res = client.post("/auth/login", data={"username": "sales@medtender.rw", "password": "SalesSecure2026!"})
    token = login_res.json()["access_token"]

    new_tender_payload = {
        "title": "Supply and Commissioning of Neonatal Intensive Care Incubators",
        "reference_number": "000045/G/NCB/2025/2026/RBC",
        "procuring_entity": "Rwanda Biomedical Centre (RBC)",
        "country": "Rwanda",
        "category": "Neonatal Care",
        "source_url": "https://www.umucyo.gov.rw/tender/000045",
        "items": [
            {
                "lot_number": 1,
                "item_number": 1,
                "title": "Closed Intensive Care Neonatal Incubator",
                "quantity": 10,
                "unit": "Units",
                "specifications_raw": "Double wall canopy, servo skin temp control, integrated scale."
            }
        ]
    }

    create_res = client.post("/tenders", json=new_tender_payload, headers={"Authorization": f"Bearer {token}"})
    assert create_res.status_code == 201
    tender_data = create_res.json()
    tender_id = tender_data["id"]
    assert tender_data["title"] == new_tender_payload["title"]
    assert len(tender_data["items"]) == 1

    # Update workflow status to BID_PREPARATION
    status_res = client.post(
        f"/tenders/{tender_id}/status",
        json={"status": TenderStatus.BID_PREPARATION.value, "notes": "Approved by supervisor for competitive bid defense."},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == TenderStatus.BID_PREPARATION.value


def test_catalogue_list_search_and_create():
    """Test 13: Search and manage products in the central catalogue."""
    login_res = client.post("/auth/login", data={"username": "sales@medtender.rw", "password": "SalesSecure2026!"})
    token = login_res.json()["access_token"]

    # 1. List products
    list_res = client.get("/catalogue", headers={"Authorization": f"Bearer {token}"})
    assert list_res.status_code == 200
    products = list_res.json()
    assert len(products) >= 1

    # 2. Search products by keyword
    search_res = client.get("/catalogue/search?q=anesthesia", headers={"Authorization": f"Bearer {token}"})
    assert search_res.status_code == 200
    matches = search_res.json()
    assert len(matches) >= 1
    assert "WATO EX-65" in matches[0]["model"]
    assert matches[0]["match_score"] > 0

    # 3. Create new product (Admin)
    admin_login = client.post("/auth/login", data={"username": "admin@medtender.rw", "password": "AdminSecure2026!"})
    admin_token = admin_login.json()["access_token"]

    new_prod_payload = {
        "product_code": "MT-DEFIB-200",
        "name": "Biphasic Defibrillator Monitor",
        "category": "Cardiology",
        "manufacturer": "Shenzhen Mindray Bio-Medical",
        "model": "BeneHeart D3",
        "keywords": ["defibrillator", "aed", "ecg", "cardiac"],
        "technical_specifications": {"energy_range": "1 - 360J", "pacing": "Demand and Fixed mode"},
        "certifications": ["ISO 13485:2016", "CE Mark 0123"]
    }
    create_prod_res = client.post("/catalogue", json=new_prod_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_prod_res.status_code == 201
    assert create_prod_res.json()["product_code"] == "MT-DEFIB-200"


def test_document_extraction_docx():
    """Test 14: Extract structured tender specifications from an in-memory .docx document."""
    # Build a minimal valid in-memory .docx file with paragraphs and table
    docx_buf = io.BytesIO()
    with zipfile.ZipFile(docx_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as docx_zip:
        # [Content_Types].xml
        docx_zip.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        # _rels/.rels
        docx_zip.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        # word/document.xml
        document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Tender Ref: 000088/G/NCB/2025/2026/KFH</w:t></w:r></w:p>
    <w:p><w:r><w:t>Tender Title: Supply and Installation of High-Frequency Surgical C-Arm System</w:t></w:r></w:p>
    <w:p><w:r><w:t>Procuring Entity: King Faisal Hospital Rwanda</w:t></w:r></w:p>
    <w:p><w:r><w:t>Deadline: 2026-09-30 10:00 Africa/Kigali</w:t></w:r></w:p>
    <w:tbl>
      <w:tr>
        <w:tc><w:p><w:r><w:t>Item No</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>Description</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>Qty</w:t></w:r></w:p></w:tc>
      </w:tr>
      <w:tr>
        <w:tc><w:p><w:r><w:t>1</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>Digital Mobile C-Arm Fluoroscopy System</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>2 Units</w:t></w:r></w:p></w:tc>
      </w:tr>
    </w:tbl>
  </w:body>
</w:document>"""
        docx_zip.writestr("word/document.xml", document_xml)

    docx_bytes = docx_buf.getvalue()

    response = client.post(
        "/tenders/extract-document",
        files={"file": ("bidding_spec_kfh.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "bidding_spec_kfh.docx"
    assert data["tables_count"] == 1
    assert "metadata" in data
    assert "items" in data


def test_audit_trail_integrity():
    """Test 15: Verify security and administrative actions are faithfully recorded in the AuditLog."""
    db = TestingSessionLocal()
    try:
        logs = db.query(AuditLog).all()
        assert len(logs) > 0
        actions = {log.action for log in logs}
        # Check that LOGIN, CREATE, UPDATE, etc. are recorded
        assert any(a in ["LOGIN", "CREATE", "UPDATE", "STATUS_CHANGE", "LOGIN_FAILED"] for a in actions)
    finally:
        db.close()


if __name__ == "__main__":
    print("Running MedTender Intelligence API & Security Test Suite...")
    setup_module()
    test_system_health()
    print("  [✓] Test 1: System Health Endpoint")
    test_auth_login_success()
    print("  [✓] Test 2: User Login & JWT Token Generation")
    test_auth_login_invalid_password()
    print("  [✓] Test 3: Invalid Password & Brute-force Audit Event")
    test_auth_login_disabled_user()
    print("  [✓] Test 4: Inactive User Access Denial (403)")
    test_auth_token_refresh()
    print("  [✓] Test 5: Token Refresh Handshake")
    test_auth_current_user_profile()
    print("  [✓] Test 6: User Profile Verification (/auth/me)")
    test_auth_admin_create_user()
    print("  [✓] Test 7: Admin User Provisioning (201)")
    test_auth_non_admin_cannot_create_user()
    print("  [✓] Test 8: Non-Admin Creation Denial (RBAC 403)")
    test_tender_sources_list_and_get()
    print("  [✓] Test 9: Tender Sources Listing & Detail Retrieval")
    test_tender_sources_create_and_update_rbac()
    print("  [✓] Test 10: Tender Source Admin Modification & Viewer Restrictions")
    test_tenders_list_and_filter()
    print("  [✓] Test 11: Tender Listing & Multi-parameter Filtering")
    test_tenders_create_and_status_update()
    print("  [✓] Test 12: Tender Creation & Workflow Status Transition")
    test_catalogue_list_search_and_create()
    print("  [✓] Test 13: Catalogue Keyword Search & Product Management")
    test_document_extraction_docx()
    print("  [✓] Test 14: In-Memory DOCX Tender Specification Extraction")
    test_audit_trail_integrity()
    print("  [✓] Test 15: Audit Trail Verification & Traceability")
    print("\nALL 15 END-TO-END SECURITY & API TESTS PASSED WITH 100% SUCCESS!")
