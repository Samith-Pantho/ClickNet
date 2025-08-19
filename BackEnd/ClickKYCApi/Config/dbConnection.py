from typing import Dict
from fastapi import WebSocket
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from contextlib import asynccontextmanager
from sqlalchemy import MetaData

meta = MetaData()

# Database URLs with connection pooling
CBS_DB_URL = (
    f"mysql+asyncmy://{os.getenv('DB_CBS_USER', 'cbs_user')}:"
    f"{os.getenv('DB_CBS_PASSWORD', 'cbs_password')}@"
    f"{os.getenv('DB_CBS_HOST', 'mysql-cbs')}:"
    f"{os.getenv('DB_CBS_PORT', '3306')}/"
    f"{os.getenv('DB_CBS_NAME', 'cbs_db')}"
    "?charset=utf8mb4"
)

CLICKKYC_DB_URL = (
    f"mysql+asyncmy://{os.getenv('DB_CLICKKYC_USER', 'clickkyc_user')}:"
    f"{os.getenv('DB_CLICKKYC_PASSWORD', 'clickkyc_password')}@"
    f"{os.getenv('DB_CLICKKYC_HOST', 'mysql-clickkyc')}:"
    f"{os.getenv('DB_CLICKKYC_PORT', '3306')}/"
    f"{os.getenv('DB_CLICKKYC_NAME', 'clickkyc_db')}"
    "?charset=utf8mb4"
)

# Create async engines with connection pooling
async_engine_cbs = create_async_engine(
    CBS_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

async_engine_clickkyc = create_async_engine(
    CLICKKYC_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create sync engines for legacy operations
sync_engine_cbs = create_engine(
    CBS_DB_URL.replace("+asyncmy", "+pymysql"),
    pool_pre_ping=True,
    pool_recycle=3600
)

sync_engine_clickkyc = create_engine(
    CLICKKYC_DB_URL.replace("+asyncmy", "+pymysql"),
    pool_pre_ping=True,
    pool_recycle=3600
)
engine = sync_engine_clickkyc
# Async session makers
AsyncSessionLocalCBS = sessionmaker(
    bind=async_engine_cbs,
    class_=AsyncSession,
    expire_on_commit=False
)

AsyncSessionLocalClickKyc = sessionmaker(
    bind=async_engine_clickkyc,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI routes
@asynccontextmanager
async def get_cbs_db():
    async with AsyncSessionLocalCBS() as session:
        try:
            yield session
        finally:
            await session.close()

@asynccontextmanager
async def get_clickkyc_db():
    async with AsyncSessionLocalClickKyc() as session:
        try:
            yield session
        finally:
            await session.close()