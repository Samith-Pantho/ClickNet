from sqlalchemy import Integer, Table, Column, String, DateTime, text
from Config.dbConnection import meta, engine

customerOTP = Table(
    "CUSTOMER_OTP", meta,
    Column("SL", Integer, primary_key=True, index=True),
    Column("DB_SVR_DT", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("PHONE_NUMBER", String(50)),
    Column("PHONE_MESSAGE", String(1000), default=""),
    Column("PHONE_OTP", String(20), default=""),
    Column("PHONE_OTP_EXPIRED_AT", DateTime),
    Column("PHONE_OTP_VERIFIED_AT", DateTime),
    Column("PHONE_SENT_AT", DateTime),
    Column("PHONE_OTP_REMARKS", String(20), default="PENDING"),
    Column("EMAIL_ADDRESS", String(50), default=""),
    Column("EMAIL_MESSAGE", String(1000), default=""),
    Column("EMAIL_OTP", String(20), default=""),
    Column("EMAIL_OTP_EXPIRED_AT", DateTime),
    Column("EMAIL_OTP_VERIFIED_AT", DateTime),
    Column("EMAIL_SENT_AT", DateTime),
    Column("EMAIL_OTP_REMARKS", String(20), default="PENDING"),
    Column("IP_ADDRESS", String(20), default="::1")
)

meta.create_all(bind=engine)
