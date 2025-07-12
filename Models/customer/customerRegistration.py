from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime
from Config.dbConnection import meta, engine

customerRegistration = Table(
    "CUST_REGISTRATION", meta,
    Column("ID", Integer, primary_key=True),
    Column("BRANCH_ID", String(20)),
    Column("BRANCH_NM", String(250), nullable=False),
    Column("ACCOUNT_NO", String(500), nullable=False),
    Column("ACCOUN_TTITLE", String(250)),
    Column("CUSTOMER_ID", String(20)),
    Column("HARDWARETOKEN", String(150)),
    Column("AUTHENTICATIONTYPE", String(50)),
    Column("PHONE_NUMBER", String(50), nullable=False),
    Column("EMAIL", String(150), nullable=False),
    Column("IMEI1", String(15), nullable=False),
    Column("IMEI2", String(15)),
    Column("REMARK", String(400)),
    Column("STATUS", Integer),
    Column("PROCESS_FLAG", Boolean),
    Column("PROCESS_BY", String(30)),
    Column("PROCESS_DT", DateTime),
    Column("CREATE_BY", String(30)),
    Column("CREATE_DT", DateTime),
    Column("UPDATE_DT", DateTime),
    Column("UPDATE_BY", String(30)),
    Column("ISCHECKED", Boolean),
    Column("CHECK_BY", String(30)),
    Column("CHECK_DT", DateTime),
    Column("ISAUTHORIZED", Boolean),
    Column("AUTHORIZE_BY", String(30)),
    Column("AUTHORIZE_DT", DateTime)
)

meta.create_all(bind=engine)