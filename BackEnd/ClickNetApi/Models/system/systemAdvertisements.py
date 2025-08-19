
from sqlalchemy import Boolean, Integer, Table, Column, String
from Config.dbConnection import meta, engine

systemAdvertisements = Table(
    "SYSTEM_ADVERTISEMENTS", meta,
    Column("SL", Integer, primary_key=True, autoincrement=False),
    Column("TITLE", String(100)),
    Column("IMAGE_URL", String(100)),
    Column("TARGET_URL", String(1000)),
    Column("STATUS", Boolean)
)


meta.create_all(bind=engine)