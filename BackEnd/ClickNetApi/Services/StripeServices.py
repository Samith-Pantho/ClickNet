from datetime import datetime
import os
import traceback
import uuid
from Services.GenericCRUDServices import GenericInserter
from Models.shared import customerAddMoney
from Schemas.shared import SystemLogErrorSchema, AddMoneyViewModelSchema, CustomerUserProfileSchema, CustomerAddMoneySchema
from .LogServices import AddLogOrError
from .CommonServices import ApiCall, GetCurrentActiveSession, GetTableSl, GetSha1Hash
from Cache.AppSettingsCache import Get

APIWEBHOOK_URL = os.getenv("APIWEBHOOK_URL", "http://apiwebhook:9999")

async def InitializeStripPaymentSession(data:AddMoneyViewModelSchema, currentUser:CustomerUserProfileSchema) -> str:
    try:
        session = await GetCurrentActiveSession(currentUser.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        success_key = await GetSha1Hash(f"{str(uuid.uuid4())}#{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        failed_key = await GetSha1Hash(f"{str(uuid.uuid4())}#{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        amount_in_cents = int(data.Amount * 100)
        payload = {
            "ToAccountNo": data.ToAccountNo,
            "ReceiverName": data.ReceiverName,
            "Amount_in_cents": amount_in_cents,
            "Currency": data.Currency,
            "Success_key": success_key,
            "Failed_key": failed_key
        }
        headers = {
            "accept": "application/json",
            "x-api-key":  Get("API_WEBHOOK_KEY"),
            "content-type": "application/json"
        }
        
        status = await ApiCall(
            method="POST",
            url=f"{APIWEBHOOK_URL}/Webhook/InitializeStripSession",
            headers=headers,
            payload=payload
        )
        stripeSession = status.get("Result")
        
        if stripeSession:
            newStripeSession = CustomerAddMoneySchema(
                id= await GetTableSl("customerAddMoney"),
                user_id=session.user_id.lower(),
                session_id=session.session_id,
                receiver_no=data.ToAccountNo,
                receiver_name=data.ReceiverName,
                payment_via="STRIPE",
                amount_in_cent=amount_in_cents,
                currency=data.Currency or 'USD',
                payment_id=stripeSession.get("id"),
                create_dt=datetime.now(),
                success_secret_key= success_key,
                failed_secret_key=failed_key
            )
            
            await GenericInserter[CustomerAddMoneySchema].insert_record(
                table=customerAddMoney,
                schema_model=CustomerAddMoneySchema,
                data=newStripeSession,
                returning_fields=[]
            )
            
            return stripeSession.get("id")
        else:
            raise ValueError("Failed to Initialize Strip payment.")

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="StripeServices/InitializeStripPaymentSession",
            CreatedBy=""
        ))
        return None
    
