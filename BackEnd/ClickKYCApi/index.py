import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes.AppConfigRoutes import AppConfigRoutes
from Routes.InternalRoutes import InternalRoutes

from Services.CallClickKycSPServices import sp_get_all_app_settings
from Cache.AppSettingsCache import Set


from Config.dbConnection import (
    async_engine_cbs,
    async_engine_clickkyc,
    sync_engine_cbs,
    sync_engine_clickkyc,
    AsyncSessionLocalCBS,
    AsyncSessionLocalClickKyc
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with async_engine_cbs.connect():
        print("CBS database connection established")

    async with async_engine_clickkyc.connect():
        print("ClickKYC database connection established")

    # Load APP_SETTINGS into memory
    try:
        async with AsyncSessionLocalClickKyc() as session:
            rows = await sp_get_all_app_settings(session)
            settings = {row["KEY"]: row["VALUE"] for row in rows}
            Set(settings)
            print("App settings loaded into memory")
    except Exception as e:
        print(f"Failed to load app settings: {e}")

    yield

    # Shutdown
    await async_engine_clickkyc.dispose()
    await async_engine_cbs.dispose()
    print("Database connections closed")

app = FastAPI(
    title="ClickKYC API",
    description="KYC system API",
    version="1.0.0",
    lifespan=lifespan
)

# Include all routers
app.include_router(AppConfigRoutes)
app.include_router(InternalRoutes)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            
    allow_credentials=True,
    allow_methods=["*"],             
    allow_headers=["*"],             
)


@app.get("/health")
async def health_check():
    return {
        "status": "API is running",
        "database_status": {
            "cbs": "connected",
            "clickkyc": "connected"
        }
    }