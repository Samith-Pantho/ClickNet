from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from Config.dbConnection import meta, engine

customerChatSessions = Table(
    "CUSTOMER_CHAT_SESSIONS", meta,
    Column("SESSION_ID", String(500), primary_key=True),
    Column("USER_ID", String(50)),
    Column("STARTED_AT", DateTime, default=datetime.now)
)


meta.create_all(bind=engine)
