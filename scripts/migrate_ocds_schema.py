"""
Idempotent Database Schema Migration for OCDS & Umucyo Two-Tier Ingestion
========================================================================
Applies necessary column additions and indices to support OCDS releases,
payloads, and portal adv_no / adv_status tracking without data loss.
"""
import sys
import logging
from sqlalchemy import inspect, text
from app.database import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("schema_migration")


def run_migration():
    logger.info("Starting database schema migration for OCDS integration...")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if "tenders" not in existing_tables:
        logger.info("Tables not found. Creating all tables from metadata...")
        from app.database import Base
        import app.models  # load all models
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully.")
        return

    # Check and add columns to 'tenders'
    tender_cols = {col["name"]: col for col in inspector.get_columns("tenders")}
    new_tender_columns = [
        ("ocid", "VARCHAR(255)"),
        ("ocds_release_id", "VARCHAR(255)"),
        ("ocds_payload", "TEXT"),
        ("portal_adv_no", "VARCHAR(100)"),
        ("portal_adv_status", "VARCHAR(50)"),
    ]

    with engine.begin() as conn:
        for col_name, col_type in new_tender_columns:
            if col_name not in tender_cols:
                logger.info(f"Adding column 'tenders.{col_name}' ({col_type})...")
                conn.execute(text(f"ALTER TABLE tenders ADD COLUMN {col_name} {col_type}"))
            else:
                logger.info(f"Column 'tenders.{col_name}' already exists. Skipping.")

        # Create indices if on SQLite / Postgres
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tenders_ocid ON tenders (ocid)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tenders_portal_adv_no ON tenders (portal_adv_no)"))
        except Exception as e:
            logger.warning(f"Index creation note: {e}")

        # Check and add columns to 'tender_sources'
        source_cols = {col["name"]: col for col in inspector.get_columns("tender_sources")}
        new_source_columns = [
            ("code", "VARCHAR(100)"),
            ("url", "VARCHAR(500)"),
            ("scraper_type", "VARCHAR(100)"),
        ]
        for col_name, col_type in new_source_columns:
            if col_name not in source_cols:
                logger.info(f"Adding column 'tender_sources.{col_name}' ({col_type})...")
                conn.execute(text(f"ALTER TABLE tender_sources ADD COLUMN {col_name} {col_type}"))
            else:
                logger.info(f"Column 'tender_sources.{col_name}' already exists. Skipping.")

        # Check and add columns to 'tender_items'
        item_cols = {col["name"]: col for col in inspector.get_columns("tender_items")}
        new_item_columns = [
            ("lot_number", "INTEGER"),
            ("item_number", "INTEGER"),
            ("title", "VARCHAR(500)"),
            ("specifications_raw", "TEXT"),
        ]
        for col_name, col_type in new_item_columns:
            if col_name not in item_cols:
                logger.info(f"Adding column 'tender_items.{col_name}' ({col_type})...")
                conn.execute(text(f"ALTER TABLE tender_items ADD COLUMN {col_name} {col_type}"))
            else:
                logger.info(f"Column 'tender_items.{col_name}' already exists. Skipping.")

    logger.info("Schema migration completed successfully.")


if __name__ == "__main__":
    run_migration()
