from sqlalchemy import Boolean, DateTime, Table, Column, String, Date, MetaData, Text
from Config.dbConnection import meta, engine

customerRegistration = Table(
    "CUSTOMER_REGISTRATION", meta,
    Column("TRACKING_ID", String(100), primary_key=True),
    
    # Personal Information
    Column("NAME", String(500)),
    Column("TITLE", String(50)),
    Column("FIRST_NAME", String(100)),
    Column("MIDDLE_NAME", String(100)),
    Column("LAST_NAME", String(100)),
    Column("SUFFIX", String(50)),
    Column("BIRTH_DATE", Date),
    Column("TAX_ID", String(50)),
    Column("TAX_ID_TYPE", String(100)),
    Column('IS_TAX_ID_VERIFIED', Boolean),
    Column("VERIFICATION_SESSION_ID", String(500)),
    
    # Address Information
    Column("ADDRESS_TYPE", String(100)),
    Column("LINE_1", String(500)),
    Column("LINE_2", String(500)),
    Column("LINE_3", String(500)),
    Column("LINE_4", String(500)),
    Column("CITY", String(100)),
    Column("STATE_CODE", String(100)),
    Column("ZIPCODE", String(200)),
    Column("COUNTRY_CODE", String(100)),
    
    # Contact Information
    Column("EMAIL_ADDRESS", String(500)),
    Column("PHONE_NUMBER", String(200), nullable=False),
    
    # Account Information
    Column("PRODUCT_CODE", String(50), nullable=False),
    Column("BRANCH_CODE", String(50)),
    Column("CUSTOMER_ID", String(100)),
    Column("ACCOUNT_NUMBER", String(100)),
    
    # Additional columns to match your style
    Column("CREATE_BY", String(30)),
    Column("CREATE_DT", DateTime),
    Column("STATUS", String(30)),
    Column("REJECT_REASON", Text)
)

meta.create_all(bind=engine)