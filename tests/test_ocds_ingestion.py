"""
Tests for OCDS Ingestion, Parameterized Deep Links, and Dead-Letter Queue
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.tender import Tender, TenderItem
from app.models.tender_source import TenderSource
from app.services.ocds_service import (
    build_safe_portal_url,
    map_release_to_tender_payload,
    sync_ocds_tenders,
    record_dead_letter,
    DEAD_LETTER_FILE,
    get_verified_ocds_sample_releases,
    OCDSClient,
)


@pytest.fixture
def memory_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_build_safe_portal_url():
    """Verify that URL generator includes mandatory query parameters and escapes values."""
    url = build_safe_portal_url("000003/G/ICB/2026/2027/1605000000", "00")
    assert "https://www.umucyo.gov.rw/eb/bav/selectAdvertisingDtlInfo.do" in url
    assert "adv_no=000003" in url
    assert "adv_status=00" in url
    assert not url.endswith("selectAdvertisingDtlInfo.do")


def test_map_release_to_tender_payload():
    """Verify standard OCDS JSON release is cleanly mapped to internal schema."""
    release = get_verified_ocds_sample_releases()[0]
    payload = map_release_to_tender_payload(release)

    assert payload["ocid"] == release["ocid"]
    assert payload["reference_number"] == release["tender"]["id"]
    assert payload["title"] == release["tender"]["title"]
    assert payload["procuring_entity"] == release["buyer"]["name"]
    assert float(payload["tender_value"]) == 34643704.51
    assert payload["currency"] == "RWF"
    assert "adv_no=" in payload["source_url"]
    assert "adv_status=00" in payload["source_url"]
    assert len(payload["items"]) >= 1


def test_idempotent_sync(memory_db):
    """Verify that sync operations are strictly idempotent (no duplicates created)."""
    samples = get_verified_ocds_sample_releases()

    with patch.object(OCDSClient, "fetch_releases", return_value=samples):
        # 1. First sync run
        result1 = sync_ocds_tenders(db=memory_db, limit=10)
        assert result1["new_tenders_created"] == 3
        assert result1["tenders_updated"] == 0

        count_after_first = memory_db.query(Tender).count()
        assert count_after_first == 3

        # 2. Second sync run with identical releases
        result2 = sync_ocds_tenders(db=memory_db, limit=10)
        assert result2["new_tenders_created"] == 0
        assert result2["tenders_updated"] == 3

        count_after_second = memory_db.query(Tender).count()
        assert count_after_second == 3  # Count must remain unchanged!


def test_dead_letter_logging():
    """Verify non-200 responses and errors are recorded without crashes."""
    record = record_dead_letter(
        endpoint="https://www.umucyo.gov.rw/eb/bav/selectAdvertisingDtlInfo.do",
        status_code=500,
        error_message="Internal Server Error: Missing adv_no query param",
        context={"test": True},
    )

    assert record is not None
    assert record["status_code"] == 500
    assert "selectAdvertisingDtlInfo.do" in record["endpoint"]
    assert record["error"] == "Internal Server Error: Missing adv_no query param"
