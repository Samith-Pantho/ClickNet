from sqlalchemy import Integer, Table, Column, String, DateTime, JSON, ForeignKey, Text
from Config.dbConnection import meta, engine

diditIdVerifications = Table(
    "DIDIT_ID_VERIFICATIONS", meta,
    Column("session_id", String(100), ForeignKey("DIDIT_SESSIONS.session_id"), primary_key=True, index=True),
    Column("address", Text),
    Column("age", Integer),
    Column("back_image", Text),
    Column("back_video", Text),
    Column("date_of_birth", DateTime),
    Column("date_of_issue", DateTime),
    Column("document_number", String(100)),
    Column("document_type", String(100)),
    Column("expiration_date", DateTime),
    Column("extra_fields", JSON),
    Column("extra_files", JSON),
    Column("first_name", String(100)),
    Column("formatted_address", Text),
    Column("front_image", Text),
    Column("front_video", Text),
    Column("full_back_image", Text),
    Column("full_front_image", Text),
    Column("full_name", String(255)),
    Column("gender", String(50)),
    Column("issuing_state", String(100)),
    Column("issuing_state_name", String(100)),
    Column("last_name", String(100)),
    Column("marital_status", String(50)),
    Column("nationality", String(100)),
    Column("parsed_address", Text),
    Column("personal_number", String(100)),
    Column("place_of_birth", String(255)),
    Column("portrait_image", Text),
    Column("status", String(50)),
    Column("warnings", JSON),
)

# Create all tables
meta.create_all(bind=engine)
