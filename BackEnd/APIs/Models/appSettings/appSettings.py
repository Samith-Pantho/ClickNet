from sqlalchemy import Table, Column, String
from Config.dbConnection import meta, engine

appSettings = Table(
    "APP_SETTINGS", meta,
    Column("KEY", String(255), primary_key=True),
    Column("DESCRIPTION", String(3000)),
    Column("PRIVACYLEVEL", String(1)),
    Column("VALUE", String(1000), nullable=False),
)

meta.create_all(bind=engine)