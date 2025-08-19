from sqlalchemy import Boolean, Integer, Table, Column, String
from Config.dbConnection import meta, engine

systemCaptchaLog = Table(
    "SYSTEM_CAPTCHA_LOG", meta,
    Column("SL", Integer, primary_key=True, autoincrement=False),
    Column("UUID", String(100), unique=True),
    Column("STATUS", Boolean)
)


meta.create_all(bind=engine)