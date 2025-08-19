from typing import Dict
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from contextlib import asynccontextmanager
from sqlalchemy import MetaData

meta = MetaData()

CLICKKYC_DB_URL = (
    f"mysql+asyncmy://{os.getenv('DB_CLICKKYC_USER', 'clickkyc_user')}:"
    f"{os.getenv('DB_CLICKKYC_PASSWORD', 'clickkyc_password')}@"
    f"{os.getenv('DB_CLICKKYC_HOST', 'mysql-clickkyc')}:"
    f"{os.getenv('DB_CLICKKYC_PORT', '3306')}/"
    f"{os.getenv('DB_CLICKKYC_NAME', 'clickkyc_db')}"
    "?charset=utf8mb4"
)



async_engine_clickkyc = create_async_engine(
    CLICKKYC_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

sync_engine_clickkyc = create_engine(
    CLICKKYC_DB_URL.replace("+asyncmy", "+pymysql"),
    pool_pre_ping=True,
    pool_recycle=3600
)
engine = sync_engine_clickkyc

AsyncSessionLocalClickKyc = sessionmaker(
    bind=async_engine_clickkyc,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_clickkyc_db():
    async with AsyncSessionLocalClickKyc() as session:
        try:
            yield session
        finally:
            await session.close()