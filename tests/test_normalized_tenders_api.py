import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal, get_db
from app.main import app
from app.models.tender import Tender, TenderItem
from app.core.enums import TenderStatus


@pytest.fixture
def client():
    return TestClient(app)


def test_public_tenders_list_normalized_schema(client):
    """Ensure GET /tenders is accessible publicly and returns the normalized OCDS schema."""
    response = client.get("/tenders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first = data[0]
    # Verify required normalized OCDS fields
    assert "id" in first
    assert "tenderNo" in first
    assert "title" in first
    assert "description" in first
    assert "procuringEntity" in first
    assert "status" in first
    assert "publicationDate" in first
    assert "submissionDeadline" in first
    assert "estimatedValue" in first
    assert "documents" in first

    # Verify estimatedValue structure
    est = first["estimatedValue"]
    assert "amount" in est
    assert "currency" in est
    assert "formatted" in est
    assert isinstance(est["formatted"], str)

    # Verify response headers
    assert "X-Total-Count" in response.headers
    assert "X-Page" in response.headers


def test_api_tenders_alias_and_search(client):
    """Ensure /api/tenders endpoint works and multi-field search operates properly."""
    # Test /api/tenders alias
    alias_res = client.get("/api/tenders")
    assert alias_res.status_code == 200
    assert len(alias_res.json()) >= 1

    # Test search query
    search_res = client.get("/tenders?q=hospital")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert isinstance(search_data, list)
    for item in search_data:
        combined = f"{item['title']} {item['procuringEntity']} {item['tenderNo']} {item['description']}".lower()
        assert "hospital" in combined


def test_paginated_tenders_endpoint(client):
    """Ensure paginated=true returns the wrapped PaginatedTendersOut schema."""
    response = client.get("/tenders?paginated=true&page=1&page_size=3")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data

    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["items"]) <= 3
    assert data["total"] >= len(data["items"])


def test_tender_lookup_by_ocid_or_ref(client):
    """Ensure single tender detail can be looked up by OCID, reference_number, or UUID."""
    # First get a tender to know its ID and reference
    list_res = client.get("/tenders")
    first = list_res.json()[0]

    tender_id = first["id"]
    detail_res = client.get(f"/tenders/{tender_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == tender_id
    assert detail["tenderNo"] == first["tenderNo"]
    assert detail["procuringEntity"] == first["procuringEntity"]


def test_tenders_status_filter(client):
    """Ensure filtering by status works correctly."""
    response = client.get("/tenders?status=active")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    for item in items:
        assert item["status"].lower() in ["active", "new"]
