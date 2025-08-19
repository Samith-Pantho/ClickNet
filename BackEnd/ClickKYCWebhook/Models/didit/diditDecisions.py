from sqlalchemy import Integer, Table, Column, String, DateTime, JSON, ForeignKey, Text
from Config.dbConnection import meta, engine

diditDecisions = Table(
    "DIDIT_DECISIONS", meta,
    Column("session_id", String(100), ForeignKey("DIDIT_SESSIONS.session_id"), primary_key=True, index=True),
    Column("aml", String(255)),
    Column("callback", Text),
    Column("contact_details", String(255)),
    Column("created_at", DateTime),
    Column("database_validation", String(255)),
    Column("expected_details", String(255)),
    Column("metadata", JSON),
    Column("nfc", String(255)),
    Column("phone", String(255)),
    Column("poa", String(255)),
    Column("reviews", JSON),
    Column("status", String(50)),
    Column("vendor_data", String(100)),
    Column("workflow_id", String(100)),
    Column("session_url", String(255)),
    Column("session_number", Integer),
)

# Create all tables
meta.create_all(bind=engine)
