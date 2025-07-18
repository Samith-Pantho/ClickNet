from sqlalchemy import Table, Column, String, DateTime, Numeric, Integer, MetaData
from Config.dbConnection import meta, engine

customerSession = Table(
    "CUSTOMER_SESSION", meta,
    
    Column("USER_ID", String(250), nullable=False),
    Column("SESSION_ID", String(500), primary_key=True),
    Column("START_TIME", DateTime, nullable=False),
    Column("LAST_ACCESS_TIME", DateTime),
    Column("IP_ADDRESS", String(20), nullable=False),
    Column("ACTIVE_FLAG", Numeric, nullable=False),
    Column("REMARKS", String(255)),
    Column("STATUS", Integer, nullable=False),
    Column("CREATE_BY", String(30)),
    Column("CREATE_DT", DateTime),
)

meta.create_all(bind=engine)
