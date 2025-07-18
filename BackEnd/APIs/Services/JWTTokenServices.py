from datetime import datetime, timedelta
from typing import Optional
import uuid
import jwt
from sqlalchemy import and_, desc, func, select
from Config.dbConnection import engine 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Models.shared import customerUserProfile, customerSession
from Schemas.shared import SystemLogErrorSchema, CustomerUserProfileSchema
from .LogServices import AddLogOrError
from .AppSettingsServices import FetchAppSettingsByKey
from .CommonServices import GetDecryptedText, GetEncryptedText

jwt_secret_key = FetchAppSettingsByKey("JWT_SECRET_KEY")
access_token_time = float(FetchAppSettingsByKey("ACCESS_TOKEN_TIME"))

security = HTTPBearer()

def ValidateJWTToken(credentials: HTTPAuthorizationCredentials) -> CustomerUserProfileSchema:
    now_date = datetime.now()
    expiry_date = now_date
    valid_user = CustomerUserProfileSchema()
    session_id = ""

    try:
        token = credentials.credentials
        payload = jwt.decode(token, jwt_secret_key, algorithms=["HS256"])
        
        user_id = GetDecryptedText(payload.get("UserId"))
        expiry_date_str = payload.get("ExpiryDate")
        if expiry_date_str:
            expiry_date = datetime.strptime(expiry_date_str, "%d-%b-%Y")
        session_id = GetDecryptedText(payload.get("SessionID"))

    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "JWTTokenServices/ValidateJWTToken",
            CreatedBy = ""
        ))
        raise ValueError("Valid token required")

    if not user_id or not session_id:
        raise ValueError("Valid token required")

    if now_date > expiry_date:
        raise ValueError("Token expired")

    if user_id:
        with engine.connect() as _conn:
            result = _conn.execute(customerUserProfile.select().where(func.lower(customerUserProfile.c.USER_ID) == user_id.lower())).first()
        
            if result:
                valid_user = CustomerUserProfileSchema(**dict(result._mapping))
            else:
                valid_user = None

        if valid_user:
            check_active_session = customerSession()
            with engine.connect() as _conn:
                result = _conn.execute(
                    select(customerSession)
                    .where(
                        and_(
                            func.lower(customerSession.c.UserId) == func.lower(user_id),
                            customerSession.c.ACTIVE_FLAG == 1,
                            customerSession.c.SESSION_ID ==  session_id
                        )
                    )
                    .order_by(desc(customerSession.c.START_TIME)) 
                    .limit(1)
                ).fetchone()

                if result:
                    check_active_session = CustomerUserProfileSchema(**dict(result._mapping))
                else:
                    check_active_session + None
            
            if check_active_session:
                return valid_user
            else:
                raise ValueError("Token deactivated")
        else:
            raise ValueError("Invalid token")
    raise ValueError("Invalid token")

def GenerateJWTToken(user_id:str, ip_address:str) -> str:
    algorithm = "HS256"
    
    start_date = datetime.now()
    expiry_date = start_date + timedelta(minutes=access_token_time)

    payload = {
        "UserId": GetEncryptedText(user_id.lower()),
        "SessionID": GetEncryptedText(f"{str(uuid.uuid4())}#{start_date.strftime("%Y-%m-%d %H:%M:%S")}"),
        "IpAddress": ip_address,
        "StartDate": start_date.isoformat(),
        "ExpiryDate": expiry_date.isoformat()
    }

    token = jwt.encode(
        payload,
        jwt_secret_key,
        algorithm=algorithm
    )

    return token