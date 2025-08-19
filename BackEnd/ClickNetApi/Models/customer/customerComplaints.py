from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Enum
from Config.dbConnection import meta, engine
from datetime import datetime

customerComplaints = Table(
    "CUSTOMER_COMPLAINTS", meta,
    Column("ID", Integer, primary_key=True, autoincrement=False),
    Column("USER_ID", String(100), nullable=False),
    Column("CATEGORY", String(100)),
    Column("DESCRIPTION", Text),
    Column("STATUS", String(20), default="OPEN"),  # OPEN, IN_PROGRESS, RESOLVED
    Column("RESPONSE", Text),
    Column("CREATED_AT", DateTime, default=datetime.now),
    Column("UPDATED_AT", DateTime, default=datetime.now, onupdate=datetime.now)
)
meta.create_all(bind=engine)
