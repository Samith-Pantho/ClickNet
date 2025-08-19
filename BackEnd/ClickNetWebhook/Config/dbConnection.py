from typing import Dict
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from contextlib import asynccontextmanager
from sqlalchemy import MetaData

meta = MetaData()

CBS_DB_URL = (
    f"mysql+asyncmy://{os.getenv('DB_CBS_USER', 'cbs_user')}:"
    f"{os.getenv('DB_CBS_PASSWORD', 'cbs_password')}@"
    f"{os.getenv('DB_CBS_HOST', 'mysql-cbs')}:"
    f"{os.getenv('DB_CBS_PORT', '3306')}/"
    f"{os.getenv('DB_CBS_NAME', 'cbs_db')}"
    "?charset=utf8mb4"
)

CLICKNET_DB_URL = (
    f"mysql+asyncmy://{os.getenv('DB_CLICKNET_USER', 'clicknet_user')}:"
    f"{os.getenv('DB_CLICKNET_PASSWORD', 'clicknet_password')}@"
    f"{os.getenv('DB_CLICKNET_HOST', 'mysql-clicknet')}:"
    f"{os.getenv('DB_CLICKNET_PORT', '3306')}/"
    f"{os.getenv('DB_CLICKNET_NAME', 'clicknet_db')}"
    "?charset=utf8mb4"
)

async_engine_cbs = create_async_engine(
    CBS_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

async_engine_clicknet = create_async_engine(
    CLICKNET_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

sync_engine_cbs = create_engine(
    CBS_DB_URL.replace("+asyncmy", "+pymysql"),
    pool_pre_ping=True,
    pool_recycle=3600
)

sync_engine_clicknet = create_engine(
    CLICKNET_DB_URL.replace("+asyncmy", "+pymysql"),
    pool_pre_ping=True,
    pool_recycle=3600
)
engine = sync_engine_clicknet

AsyncSessionLocalCBS = sessionmaker(
    bind=async_engine_cbs,
    class_=AsyncSession,
    expire_on_commit=False
)

AsyncSessionLocalClicknet = sessionmaker(
    bind=async_engine_clicknet,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_cbs_db():
    async with AsyncSessionLocalCBS() as session:
        try:
            yield session
        finally:
            await session.close()
            
@asynccontextmanager
async def get_clickkyc_db():
    async with AsyncSessionLocalClicknet() as session:
        try:
            yield session
        finally:
            await session.close()