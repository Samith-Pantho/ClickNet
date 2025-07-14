from sqlalchemy import Table, Column, String, Numeric, DateTime, Integer, text
from Config.dbConnection import meta, engine

customerOTP = Table(
    "CUSTOMER_OTP", meta,
    Column("OTP_SL", Integer, primary_key=True, autoincrement=True, index=True),
    Column("USER_ID", String(25), nullable=False),
    Column("CUST_ID", String(20), nullable=False),
    Column("DB_SVR_DT", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("PHONE_NUMBER", String(50), default=""),
    Column("EMAIL_ADDRESS", String(50), default=""),
    Column("VERIFICATION_CHANNEL", String(50), default=""),
    Column("MESSAGE", String(1000), default=""),
    Column("OTP", String(20), default=""),
    Column("OTP_EXPIRED_AT", DateTime),
    Column("OTP_VERIFIED_AT", DateTime),
    Column("SENT_AT", DateTime),
    Column("FROM_ACCOUNT_NO", String(500), nullable=False, default="00000000000"),
    Column("FROM_BRANCH_ID", String(6), nullable=False, default="0000"),
    Column("TO_ACCOUNT_NO", String(500), nullable=False, default="00000000000"),
    Column("TO_BRANCH_ID", String(12), nullable=False, default="0000"),
    Column("TO_BANK_ID", String(6), default="0000"),
    Column("TO_ROUTING_NUMB", String(9), default="000000000"),
    Column("IP_ADDRESS", String(20), nullable=False, default="::1"),
    Column("AMOUNT_CCY", Numeric(17, 4), default=0.0),
    Column("AMOUNT_LCY", Numeric(17, 4), default=0.0),
    Column("TRANSFER_TYPE", String(50), nullable=False),
    Column("PURPOSE_OF_TRANSACTION", String(500), default=""),
    Column("RECEIVER_ID", String(15), default=""),
    Column("RECEIVER_NM", String(22), default=""),
    Column("REMARKS", String(500), default=""),
)

meta.create_all(bind=engine)
