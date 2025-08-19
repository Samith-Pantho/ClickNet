import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from Routes.AppConfigRoutes import AppConfigRoutes
from Routes.RegistrationRoutes import RegistrationRoutes
from Routes.LogInRoutes import LogInRoutes
from Routes.UserIdPasswordRoutes import UserIdPasswordRoutes
from Routes.AccountRoutes import AccountRoutes
from Routes.TransactionRoutes import TransactionRoutes
from Routes.ProfileRoutes import ProfileRoutes
from Routes.ComplaintRoutes import ComplaintRoutes
from Routes.ChatRoutes import ChatRoutes
from Routes.LogOutRoutes import LogOutRoutes
from Routes.AddMoneyRoutes import AddMoneyRoutes

from Routes.WebSocketRoutes import WebSocketRoutes

from Services.CallClickNetSPServices import sp_get_all_app_settings
from Cache.AppSettingsCache import Set
from Workers.ChatWithOpenAiWorkerService import ConsumeChatRequests
from Workers.NotificationSendingWorkerService import ConsumeNotificationRequests


from Config.dbConnection import (
    async_engine_cbs,
    async_engine_clicknet,
    sync_engine_cbs,
    sync_engine_clicknet,
    AsyncSessionLocalCBS,
    AsyncSessionLocalClickNet
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with async_engine_cbs.connect():
        print("CBS database connection established")

    async with async_engine_clicknet.connect():
        print("ClickNet database connection established")

    # Load APP_SETTINGS into memory
    try:
        async with AsyncSessionLocalClickNet() as session:
            rows = await sp_get_all_app_settings(session)
            settings = {row["KEY"]: row["VALUE"] for row in rows}
            Set(settings)
            print("App settings loaded into memory")
    except Exception as e:
        print(f"Failed to load app settings: {e}")

    # Start background Kafka consumer
    asyncio.create_task(ConsumeChatRequests())
    asyncio.create_task(ConsumeNotificationRequests())

    yield

    # Shutdown
    await async_engine_clicknet.dispose()
    await async_engine_cbs.dispose()
    print("Database connections closed")

app = FastAPI(
    title="ClickNet API",
    description="Online banking system API",
    version="1.0.0",
    lifespan=lifespan
)

# Include all routers
app.include_router(AppConfigRoutes)
app.include_router(RegistrationRoutes)
app.include_router(LogInRoutes)
app.include_router(UserIdPasswordRoutes)
app.include_router(AccountRoutes)
app.include_router(TransactionRoutes)
app.include_router(ProfileRoutes)
app.include_router(ComplaintRoutes)
app.include_router(ChatRoutes)
app.include_router(LogOutRoutes)
app.include_router(AddMoneyRoutes)

app.include_router(WebSocketRoutes)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],               # leave empty
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
            "clicknet": "connected"
        }
    }