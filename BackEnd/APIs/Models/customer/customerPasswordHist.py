from sqlalchemy import Table, Column, String, Integer, Boolean, DateTime, MetaData, PrimaryKeyConstraint
from Config.dbConnection import meta, engine

customerPasswordHist = Table(
    "CUSTOMER_PASSWORD_HIST", meta,

    Column("USER_ID", String(30), nullable=False),
    Column("PASSWARD_STRING", String(300), nullable=False),
    Column("STATUS", Integer),
    Column("CREATE_BY", String(30)),
    Column("CREATE_DT", DateTime, nullable=False),

    PrimaryKeyConstraint("USER_ID", "CREATE_DT")
)

# Create the table
meta.create_all(bind=engine)
