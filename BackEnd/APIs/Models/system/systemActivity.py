from sqlalchemy import Table, Column, String, Integer, Numeric, Date, MetaData
from Config.dbConnection import meta, engine

systemActivity = Table(
    "SYSTEM_ACTIVITY", meta,
    
    Column("SL", Integer, primary_key=True, autoincrement=True),
    Column("ACTIVITY_TYPE", String(50), index=True), 
    Column("ACTIVITY_TITLE", String(100), nullable=False),
    Column("ACTIVITY_DETAILS", String(600), nullable=False),
    Column("ACTIVITY_DT", Date, index=True),
    Column("REQUESTED_FROM", String(10), nullable=False),
    Column("USER_TYPE", String(50)),
    Column("USER_ID", String(50), nullable=False)
)

# Create the table in the DB
meta.create_all(bind=engine)
