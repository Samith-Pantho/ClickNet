import time
import traceback
from fastapi import APIRouter, Request, HTTPException, status
import hmac
import hashlib
import os
from Config.dbConnection import AsyncSessionLocalClickKyc
from sqlalchemy.ext.asyncio import AsyncSession
from Schemas.shared import DiditVerificationViewModelSchema, SystemLogErrorSchema, StatusResult
from Services.CommonServices import GetErrorMessage
from Services.CustomerDataServices import UpdateCustomerRegistrationData
from Services.DigitServices import CreateDiditSession, DiditProcessWebhookData, FetchDiditData
from Services.LogServices import AddLogOrError
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from Cache.AppSettingsCache import Get
from slowapi import Limiter
from slowapi.util import get_remote_address

# Load environment variables
load_dotenv()

limiter = Limiter(key_func=get_remote_address)

WebhookRoutes = APIRouter(prefix="/Webhook")

@WebhookRoutes.post("/DiditVerificationWebhook")
@limiter.limit("10/minute")
async def DiditVerificationWebhook(request: Request):
    try:
        print("Webhook request came")
        # Get the raw request body as string
        body = await request.body()
        body_str = body.decode()

        # Get headers
        signature = request.headers.get("x-signature")
        timestamp = request.headers.get("x-timestamp")
        WEBHOOK_SECRET = Get('DIDIT_WEBHOOK_SECRET')

        if not all([signature, timestamp, WEBHOOK_SECRET]):
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not _VerifyDiditSignature(body_str, signature, timestamp, WEBHOOK_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
           )
        print("Webhook signature varified")
        try:
            diditWebhookData = await request.json()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        # Process data
        diditSessionId = diditWebhookData.get("session_id")
        diditSessionStatus= diditWebhookData.get("status")
        if diditSessionId and diditSessionStatus != "Not Started" and diditSessionStatus != "In Progress":
            await DiditProcessWebhookData(diditWebhookData)
            
            async with AsyncSessionLocalClickKyc() as async_session:
                diditFullData = await FetchDiditData(diditSessionId, async_session)
                await async_session.commit()
                if diditFullData:
                    await UpdateCustomerRegistrationData(diditFullData)
        
        return JSONResponse(content={"status": "success"})
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "WebhookRoutes/DiditVerificationWebhook",
            CreatedBy = ""
        ))
        
    return JSONResponse(content={"status": "failed"})

def _VerifyDiditSignature(request_body: str, signature_header: str, timestamp_header: str, secret_key: str) -> bool:
  # Check if timestamp is recent (within 5 minutes)
  timestamp = int(timestamp_header)
  current_time = int(time.time())
  if abs(current_time - timestamp) > 300:  # 5 minutes
    return False

  # Calculate expected signature
  expected_signature = hmac.new(
    secret_key.encode("utf-8"),
    request_body.encode("utf-8"),
    hashlib.sha256
  ).hexdigest()

  # Compare signatures using constant-time comparison
  return hmac.compare_digest(signature_header, expected_signature)

@WebhookRoutes.post("/InitializeDiditVerification")
async def InitializeDiditVerification(request: Request):
    status = StatusResult()
    try:
        print("Initialize Didit Verification request came")
        api_key = request.headers.get("x-api-key")
    
        if api_key != Get("DIDIT_WEBHOOK_KEY"):
            raise ValueError("Invalid API key")
        print("Initialize Didit Verification header verified")
        
        data = await request.json()
        
        status = await CreateDiditSession(data)
        print("Initialize Didit Verification Success")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "WebhookRoutes/InitializeDiditVerification",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status
