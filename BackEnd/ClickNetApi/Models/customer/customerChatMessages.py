from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from Config.dbConnection import meta, engine

customerChatMessages = Table(
    "CUSTOMER_CHAT_MESSAGES", meta,
    Column("ID", Integer, primary_key=True, autoincrement=False),
    Column("SESSION_ID", String(500)),
    Column("ROLE", String(10)),  # USER or OPENAI
    Column("MESSAGE", Text),
    Column("CREATED_AT", DateTime, default=datetime.now)
)


meta.create_all(bind=engine)
