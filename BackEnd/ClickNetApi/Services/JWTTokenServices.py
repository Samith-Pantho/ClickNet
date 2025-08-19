from datetime import datetime, timedelta
from typing import Optional
import uuid
from fastapi import Depends, HTTPException
import jwt
from sqlalchemy import and_, desc, func, select
from Config.dbConnection import AsyncSessionLocalClickNet
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Models.shared import customerUserProfile, customerSession
from Schemas.shared import SystemLogErrorSchema, CustomerUserProfileSchema, CustomoerSessionSchema
from .LogServices import AddLogOrError
from Cache.AppSettingsCache import Get
from .CommonServices import GetDecryptedText, GetEncryptedText

security = HTTPBearer()

async def  ValidateJWTToken(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CustomerUserProfileSchema:
    now_date = datetime.now()
    expiry_date = now_date
    valid_user = CustomerUserProfileSchema()
    session_id = ""
    db_session = None

    try:
        token = credentials.credentials
        payload = jwt.decode(token, Get("JWT_SECRET_KEY"), algorithms=["HS256"])
        
        user_id = await GetDecryptedText(payload.get("UserId"))
        expiry_date_str = payload.get("ExpiryDate")
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M:%S')
            
        session_id = await GetDecryptedText(payload.get("SessionID"))

        if not user_id or not session_id:
            raise HTTPException(status_code=401, detail="Valid token required")

        if now_date > expiry_date:
            raise HTTPException(status_code=401, detail="Token expired")

        if user_id:
            db_session = AsyncSessionLocalClickNet()
            result = await db_session.execute(customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == user_id.lower()))
            row = result.first()
            if row:
                valid_user = CustomerUserProfileSchema(**dict(row._mapping))
            else:
                valid_user = None

            if valid_user:
                check_active_session = CustomoerSessionSchema()
                result = await db_session.execute(
                    select(customerSession)
                    .where(
                        and_(
                            func.lower(customerSession.c.USER_ID) == func.lower(user_id),
                            customerSession.c.ACTIVE_FLAG == 1,
                            customerSession.c.SESSION_ID ==  session_id
                        )
                    )
                    .order_by(desc(customerSession.c.START_TIME)) 
                    .limit(1)
                )
                if result is not None:
                    row = result.fetchone()
                if row:
                    check_active_session = CustomoerSessionSchema(**dict(row._mapping))
                else:
                    check_active_session = None
                
                if check_active_session:
                    return valid_user
                else:
                    raise HTTPException(status_code=401, detail="Token deactivated")
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

async def  GenerateJWTToken(user_id:str, ip_address:str) -> str:
    algorithm = "HS256"
    
    start_date = datetime.now()
    expiry_date = start_date + timedelta(minutes=int(Get("ACCESS_TOKEN_TIME")))

    payload = {
        "UserId": await GetEncryptedText(user_id.lower()),
        "SessionID": await GetEncryptedText(f"{str(uuid.uuid4())}#{start_date.strftime('%Y-%m-%d %H:%M:%S')}"),
        "IpAddress": ip_address,
        "StartDate": start_date.isoformat(),
        "ExpiryDate": expiry_date.isoformat()
    }

    token = jwt.encode(
        payload,
        Get("JWT_SECRET_KEY"),
        algorithm=algorithm
    )

    return token

async def  GenerateJWTTokenFromExistingSession(data:CustomoerSessionSchema) -> str:
    algorithm = "HS256"
    
    payload = {
        "UserId": await GetEncryptedText(data.user_id.lower()),
        "SessionID": await GetEncryptedText(data.session_id),
        "IpAddress": data.ip_address,
        "StartDate": data.start_time.isoformat(),
        "ExpiryDate": (data.start_time + timedelta(minutes=int(Get("ACCESS_TOKEN_TIME")))).isoformat()
    }

    token = jwt.encode(
        payload,
        Get("JWT_SECRET_KEY"),
        algorithm=algorithm
    )

    return token