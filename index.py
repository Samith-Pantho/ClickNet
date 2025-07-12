from fastapi import FastAPI
from Routes.AppConfigRoutes import AppConfigRoutes
from Routes.RegistrationRoutes import RegistrationRoutes

app =FastAPI()

app.include_router(AppConfigRoutes)
app.include_router(RegistrationRoutes)