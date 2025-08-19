from sqlalchemy import Table, Column, String, Float, JSON, ForeignKey, Text
from Config.dbConnection import meta, engine

diditLiveness = Table(
    "DIDIT_LIVENESS", meta,
    Column("session_id", String(100), ForeignKey("DIDIT_SESSIONS.session_id"), primary_key=True, index=True),
    Column("age_estimation", Float),
    Column("method", String(100)),
    Column("reference_image", Text),
    Column("score", Float),
    Column("status", String(50)),
    Column("video_url", Text),
    Column("warnings", JSON),
)

# Create all tables
meta.create_all(bind=engine)
