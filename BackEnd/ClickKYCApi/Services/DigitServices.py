import os
import traceback
from typing import Dict, Any
from sqlalchemy import select
from Schemas.shared import SystemLogErrorSchema, StatusResult
from Services.CommonServices import ApiCall, GetErrorMessage
from Services.GenericCRUDServices import GenericInserter, GenericUpdater
from Services.JWTTokenServices import GenerateJWTToken
from .LogServices import AddLogOrError
from Cache.AppSettingsCache import Get

KYCWEBHOOK_URL = os.getenv("KYCWEBHOOK_URL", "http://kycwebhook:8888")
        
async def CreateDiditSession(tracking_id: str):
    status = StatusResult()
    try:
        access_token = await GenerateJWTToken(tracking_id)
        headers = {
            "accept": "application/json",
            "x-api-key":  Get("DIDIT_WEBHOOK_KEY"),
            "content-type": "application/json"
        }
        payload = {
            "tracking_no":tracking_id,
            "access_token":access_token
        }
        status = await ApiCall(
            method="POST",
            url=f'{KYCWEBHOOK_URL}/Webhook/InitializeDiditVerification',
            headers=headers,
            payload=payload
        )
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "DigitServices/CreateDiditSession",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
    return status
