import traceback
from fastapi import APIRouter, Request, HTTPException, status
import stripe
from Schemas.shared import SystemLogErrorSchema, StripeWebhookPayload, StatusResult
from Services.CaptchaServices import VerifyCaptchaToken
from Services.ChatWithAIServices import ProcessChat
from Services.CommonServices import GetErrorMessage
from Services.LogServices import AddLogOrError
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from Cache.AppSettingsCache import Get
from slowapi import Limiter
from slowapi.util import get_remote_address

from Services.NotificationServices import SendEmail, SendSMS
from Services.StripeServices import InitializeStripPaymentSession, StripeProcessWebhookData

# Load environment variables
load_dotenv()

limiter = Limiter(key_func=get_remote_address)

WebhookRoutes = APIRouter(prefix="/Webhook")

@WebhookRoutes.post("/InitializeStripSession")
async def InitializeStripSession(request: Request):
    status = StatusResult()
    try:
        print("Initialize Strip Session request came")
        api_key = request.headers.get("x-api-key")
    
        if api_key != Get("API_WEBHOOK_KEY"):
            raise ValueError("Invalid API key")
        print("Initialize Strip Session header verified")
        
        data = await request.json()
        
        result = await InitializeStripPaymentSession(data)
        status.Status = "OK"
        status.Message = None
        status.Result = result
        print("Initialize Strip Session OpenAI Success")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "WebhookRoutes/InitializeStripSession",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status


@WebhookRoutes.post("/StripeVerificationWebhook")
@limiter.limit("10/minute")
async def StripeVerificationWebhook(request: Request):
    try:
        payload_bytes = await request.body()
        sig_header = request.headers.get("stripe-signature")

        try:
            event = stripe.Webhook.construct_event(
                payload=payload_bytes,
                sig_header=sig_header,
                secret=Get("STRIPE_WEBHOOK_SECRET")
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        try:
            print(event["type"])
            if event["type"] == "checkout.session.completed":
                payload_dict = dict(event)
                webhook_payload = StripeWebhookPayload(**payload_dict)
                
                if await StripeProcessWebhookData(webhook_payload):
                    return JSONResponse(content={"status": "success"})
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        # Process data
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "WebhookRoutes/StripeVerificationWebhook",
            CreatedBy = ""
        ))
        
    return JSONResponse(content={"status": "failed"})

@WebhookRoutes.post("/VerifyCaptcha")
async def VerifyCaptcha(request: Request):
    status = StatusResult()
    try:
        print("Captcha Verification request came")
        api_key = request.headers.get("x-api-key")
    
        if api_key != Get("API_WEBHOOK_KEY"):
            raise ValueError("Invalid API key")
        print("Captcha Verification header verified")
        
        data = await request.json()
        
        result = await VerifyCaptchaToken(data)
        status.Status = "OK"
        status.Message = None
        status.Result = result
        print("Captcha Verification Success")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "WebhookRoutes/VerifyCaptcha",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status


@WebhookRoutes.post("/GetResponseFromOpenAI")
async def GetResponseFromOpenAI(request: Request):
    status = StatusResult()
    try:
        print("Get Response From OpenAI request came")
        api_key = request.headers.get("x-api-key")
    
        if api_key != Get("API_WEBHOOK_KEY"):
            raise ValueError("Invalid API key")
        print("Get Response From OpenAI header verified")
        
        data = await request.json()
        
        result = await ProcessChat(data)
        status.Status = "OK"
        status.Message = None
        status.Result = result
        print("Get Response From OpenAI Success")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "WebhookRoutes/GetResponseFromOpenAI",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status

@WebhookRoutes.post("/SendingSMS")
async def SendingSMS(request: Request):
    status = StatusResult()
    try:
        print("Sending SMS request came")
        api_key = request.headers.get("x-api-key")
    
        if api_key != Get("API_WEBHOOK_KEY"):
            raise ValueError("Invalid API key")
        print("Sending SMS header verified")
        
        data = await request.json()
        
        result = await SendSMS(data)
        status.Status = "OK"
        status.Message = None
        status.Result = result
        print("Sending SMS Success")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "WebhookRoutes/SendingSMS",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status

@WebhookRoutes.post("/SendingEmail")
async def SendingEmail(request: Request):
    status = StatusResult()
    try:
        print("Sending Email request came")
        api_key = request.headers.get("x-api-key")
    
        if api_key != Get("API_WEBHOOK_KEY"):
            raise ValueError("Invalid API key")
        print("Sending Email header verified")
        
        data = await request.json()
        
        result = await SendEmail(data)
        status.Status = "OK"
        status.Message = None
        status.Result = result
        print("Sending Email OpenAI Success")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "WebhookRoutes/SendingEmail",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status
