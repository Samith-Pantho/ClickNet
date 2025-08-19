from sqlalchemy import Integer, Table, Column, String, Float, JSON, ForeignKey, Text
from Config.dbConnection import meta, engine

diditFaceMatches = Table(
    "DIDIT_FACE_MATCHES", meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("session_id", String(100), ForeignKey("DIDIT_SESSIONS.session_id"), index=True),
    Column("score", Float),
    Column("source_image", Text),
    Column("source_image_session_id", String(100)),
    Column("status", String(50)),
    Column("target_image", Text),
    Column("warnings", JSON),
)

# Create all tables
meta.create_all(bind=engine)
