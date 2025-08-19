from sqlalchemy import Integer, PrimaryKeyConstraint, Table, Column, String, DateTime, JSON, ForeignKey, Text, text
from Config.dbConnection import meta, engine

diditWarnings = Table(
    "DIDIT_WARNINGS", meta,
    Column("id", Integer, autoincrement=True),
    Column("session_id", String(100), ForeignKey("DIDIT_SESSIONS.session_id"), nullable=False),
    Column("feature", String(500), nullable=False),  # e.g., "ID_VERIFICATION", "FACE_MATCH"
    Column("log_type", Text),  # e.g., "error", "warning"
    Column("short_description", Text),
    Column("long_description", Text),
    Column("risk", String(255)),
    Column("additional_data", JSON),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    PrimaryKeyConstraint("session_id", "feature")
)

# Create all tables
meta.create_all(bind=engine)
