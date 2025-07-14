from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime
from Config.dbConnection import meta, engine

customerRegistration = Table(
    "CUST_REGISTRATION", meta,
    Column("ID", Integer, primary_key=True, autoincrement=True),
    Column("BRANCH_ID", String(20), nullable=False),
    Column("BRANCH_NM", String(250), nullable=False),
    Column("USER_ID", String(255), nullable=False),
    Column("CUSTOMER_TTITLE", String(250), nullable=False),
    Column("CUSTOMER_ID", String(20), nullable=False),
    Column("TAX_ID", String(50), nullable=False),
    Column("PHONE_NUMBER", String(50), nullable=False),
    Column("EMAIL", String(150)),
    Column("BIRTH_DATE", DateTime, nullable=False),
    Column("REMARK", String(400)),
    Column("CREATE_BY", String(30)),
    Column("CREATE_DT", DateTime),
    Column("STATUS", String(30))
)

meta.create_all(bind=engine)