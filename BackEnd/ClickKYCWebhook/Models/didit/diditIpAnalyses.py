from sqlalchemy import Table, Column, String, Float, Boolean, JSON, ForeignKey
from Config.dbConnection import meta, engine

diditIpAnalyses = Table(
    "DIDIT_IP_ANALYSES", meta,
    Column("session_id", String(100), ForeignKey("DIDIT_SESSIONS.session_id"), primary_key=True, index=True),
    Column("browser_family", String(100)),
    Column("device_brand", String(100)),
    Column("device_model", String(100)),
    Column("ip_address", String(45)),
    Column("ip_city", String(100)),
    Column("ip_country", String(100)),
    Column("ip_country_code", String(10)),
    Column("ip_state", String(100)),
    Column("is_data_center", Boolean),
    Column("is_vpn_or_tor", Boolean),
    Column("isp", String(100)),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("organization", String(255)),
    Column("os_family", String(100)),
    Column("platform", String(100)),
    Column("status", String(50)),
    Column("time_zone", String(50)),
    Column("time_zone_offset", String(10)),
    Column("warnings", JSON),
    Column("locations_info", JSON),
)

# Create all tables
meta.create_all(bind=engine)
