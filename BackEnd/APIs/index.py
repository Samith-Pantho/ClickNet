from fastapi import FastAPI
from Routes.AppConfigRoutes import AppConfigRoutes
from Routes.RegistrationRoutes import RegistrationRoutes
from Routes.LogInRoutes import LogInRoutes
from Routes.UserIdPasswordRoutes import UserIdPasswordRoutes

app =FastAPI()

app.include_router(AppConfigRoutes)
app.include_router(RegistrationRoutes)
app.include_router(LogInRoutes)
app.include_router(UserIdPasswordRoutes)