from sqlalchemy import Integer, Table, Column, String, DateTime, JSON, Text, text
from Config.dbConnection import meta, engine

# Main sessions table
diditSessions = Table(
    "DIDIT_SESSIONS", meta,
    Column("session_id", String(100), primary_key=True, index=True),
    Column("session_number", Integer),
    Column("session_token", String(255)),
    Column("url", Text),
    Column("vendor_data", String(100)),
    Column("metadata", JSON),
    Column("status", String(50)),
    Column("callback", Text),
    Column("workflow_id", String(100)),
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
)
# Create all tables
meta.create_all(bind=engine)
