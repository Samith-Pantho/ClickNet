from sqlalchemy import Table, Column, String, DateTime, Integer, LargeBinary, MetaData
from Config.dbConnection import meta, engine

customerPhotos = Table(
    "CUStOMER_PHOTOS", meta,

    Column("USER_ID", String(50), primary_key=True, nullable=False),
    Column("PHOTO_PATH", String(1000), nullable=False), 
    Column("CREATE_BY", String(50)),
    Column("CREATE_AT", DateTime),
)

meta.create_all(bind=engine)