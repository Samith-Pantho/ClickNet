import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes.WebhookRoutes import WebhookRoutes

from Services.CallClickKycSPServices import sp_get_all_app_settings
from Cache.AppSettingsCache import Set


from Config.dbConnection import (
    async_engine_clickkyc,
    sync_engine_clickkyc,
    AsyncSessionLocalClickKyc
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
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
    print("Database connections closed")

app = FastAPI(
    title="ClickKYC WebHook",
    description="KYC WebHook",
    version="1.0.0",
    lifespan=lifespan
)

# Include all routers
app.include_router(WebhookRoutes)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)


@app.get("/health")
async def health_check():
    return {
        "status": "WebHook is running",
        "database_status": {
            "clickkyc": "connected"
        }
    }