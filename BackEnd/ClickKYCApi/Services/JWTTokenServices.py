from datetime import datetime, timedelta
from typing import Optional
import uuid
from fastapi import Depends, HTTPException
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Schemas.shared import SystemLogErrorSchema, CustomerRegistrationSchema
from Services.KYCServices import GetTrackingData
from .LogServices import AddLogOrError
from Cache.AppSettingsCache import Get
from .CommonServices import GetDecryptedText, GetEncryptedText

security = HTTPBearer()

async def  ValidateJWTToken(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CustomerRegistrationSchema:
    now_date = datetime.now()
    expiry_date = now_date
    session_id = ""
    db_session = None

    try:
        token = credentials.credentials
        payload = jwt.decode(token, Get("JWT_SECRET_KEY"), algorithms=["HS256"])
        
        tracking_id = await GetDecryptedText(payload.get("TrackingID"))
        expiry_date_str = payload.get("ExpiryDate")
        if expiry_date_str:
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M:%S.%f')

        if not tracking_id:
            raise HTTPException(status_code=401, detail="Valid token required")

        if now_date > expiry_date:
            raise HTTPException(status_code=401, detail="Token expired")

        if tracking_id:
            valid_user = await GetTrackingData(tracking_id)

            if valid_user:
                return valid_user
            else:
                raise HTTPException(status_code=401, detail="Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as ex:
        await AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "JWTTokenServices/ValidateJWTToken",
            CreatedBy = ""
        ))
        raise HTTPException(status_code=401, detail="Valid token required")
    finally:
            if db_session:
                await db_session.close()

async def  GenerateJWTToken(tracking_id:str) -> str:
    algorithm = "HS256"
    
    start_date = datetime.now()
    expiry_date = start_date + timedelta(minutes=int(Get("ACCESS_TOKEN_TIME")))

    payload = {
        "TrackingID": await GetEncryptedText(tracking_id),
        "StartDate": start_date.isoformat(),
        "ExpiryDate": expiry_date.isoformat()
    }

    token = jwt.encode(
        payload,
        Get("JWT_SECRET_KEY"),
        algorithm=algorithm
    )

    return token