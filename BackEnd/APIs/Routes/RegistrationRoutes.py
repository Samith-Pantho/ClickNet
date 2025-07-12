from fastapi import APIRouter, HTTPException
from Schemas.shared import StatusResult
from Schemas.System.SystemLogErrorSchema import SystemLogErrorSchema
from Services.LogServices import AddLogOrError
from Models.shared import customerRegistration
from Schemas.shared import CustomerRegistrationSchema

RegistrationRoutes = APIRouter()
