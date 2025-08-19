
from datetime import datetime
import traceback
from typing import Any, Dict
from sqlalchemy import select
import stripe
from Models.shared import customerAddMoney
from Schemas.shared import StripeWebhookPayload, CustomerAddMoneySchema
from Config.dbConnection import AsyncSessionLocalClicknet
from sqlalchemy.ext.asyncio import AsyncSession
from Cache.AppSettingsCache import Get
from Schemas.shared import SystemLogErrorSchema
from Services.CBSServices import CBSAddMoneyFromGl
from Services.CommonServices import SendFtNotification
from Services.GenericCRUDServices import GenericUpdater
from .LogServices import AddLogOrError


async def InitializeStripPaymentSession(data: Dict[str, Any]) -> str:
    stripe.api_key = Get("STRIPE_SECRET_KEY")
    try:
        stripeSession = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": data.get("Currency") or 'USD',
                            "unit_amount": data.get("Amount_in_cents"),
                            "product_data": {
                                "name": data.get("ToAccountNo"),
                                "description": data.get("ReceiverName")
                            }
                        },
                        "quantity":1
                    }
                ],
                mode="payment",
                success_url=Get("STRIPE_CALLBACK_SUCCESS_URL").replace("_data_", data.get("Success_key")),
                cancel_url=Get("STRIPE_CALLBACK_CANCEL_URL").replace("_data_", data.get("Failed_key"))
            )
        
        return stripeSession

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="StripeServices/InitializeStripPaymentSession",
            CreatedBy=""
        ))
        return None
    


async def StripeProcessWebhookData(data: StripeWebhookPayload):
    db_session = None
    try:
        db_session = AsyncSessionLocalClicknet()
        result = await db_session.execute(
            select(customerAddMoney).where(customerAddMoney.c.PAYMENT_ID == data.data.object.id)
        )
        if result is not None:
            row = result.fetchone()
            
        addmoney = CustomerAddMoneySchema(**dict(row._mapping))
        
        if addmoney:
            if data.data.object.payment_status == "paid" and data.data.object.status == "complete":
                addmoney.payment_status="SUCCESS"
                addmoney.update_dt=datetime.now()
            else:
                addmoney.payment_status="FAILED"
                addmoney.update_dt=datetime.now()
                
            await GenericUpdater.update_record(
                table=customerAddMoney,
                schema_model=CustomerAddMoneySchema,
                record_id=addmoney.id,
                update_data=addmoney,
                id_column="ID",
                exclude_fields={}
            )
            
            if data.data.object.payment_status == "paid" and data.data.object.status == "complete":
                #CBS transaction
                transaction_id = await CBSAddMoneyFromGl(addmoney)
                if transaction_id:
                    addmoney.cbs_trx_id=transaction_id
                    addmoney.trx_dt=datetime.now()
                    
                    await GenericUpdater.update_record(
                        table=customerAddMoney,
                        schema_model=CustomerAddMoneySchema,
                        record_id=addmoney.id,
                        update_data=addmoney,
                        id_column="ID",
                        exclude_fields={}
                    )
                    await SendFtNotification(addmoney, transaction_id)
                    return True
                else:
                    raise ValueError("CBS transaction fro add money failed.")
            else:
                raise ValueError("Add money processing in Stripe is failed.")
        else:
            raise ValueError("No such transaction request found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "StripeServices/StripeProcessWebhookData",
            CreatedBy = ""
        ))
        raise Exception(ex)
    finally:
        if db_session:
            await db_session.close()

    

    