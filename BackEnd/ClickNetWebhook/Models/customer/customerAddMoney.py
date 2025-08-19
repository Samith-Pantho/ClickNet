from sqlalchemy import Table, Column, String, DateTime, Numeric, Integer, MetaData
from Config.dbConnection import meta, engine

customerAddMoney = Table(
    "CUSTOMER_ADD_MONEY", meta,
    Column("ID", Integer, primary_key=True, autoincrement=False),
    
    Column("USER_ID", String(250), nullable=False),
    Column("SESSION_ID", String(500), nullable=False),
    Column("RECEIVER_NO", String(100), nullable=False),
    Column("RECEIVER_NAME", String(500), nullable=False),
    Column("PAYMENT_VIA", String(20), nullable=False),
    Column("AMOUNT_IN_CENT", Integer, nullable=False),
    Column("CURRENCY", String(20), nullable=False),
    Column("PAYMENT_ID", String(500), nullable=False, unique=True),
    Column("CREATE_DT", DateTime, nullable=False),
    Column("SUCCESS_SECRET_KEY", String(500), nullable=False),
    Column("FAILED_SECRET_KEY", String(500), nullable=False),
    Column("SUCCESS_OR_FAILED_PROCESS_DT", DateTime, nullable=True),
    Column("PAYMENT_STATUS", String(50), nullable=True),
    Column("UPDATE_DT", DateTime, nullable=True),
    Column("CBS_TRX_ID", String(500), nullable=True),
    Column("TRX_DT", DateTime, nullable=True)
)

meta.create_all(bind=engine)
