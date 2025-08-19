from datetime import datetime
import traceback
import jwt
from sqlalchemy import func, or_, select
from fastapi import APIRouter, Depends
from Schemas.Enums.Enums import ActivityType
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema, AddMoneyViewModelSchema, CustomerUserProfileSchema, StatusResult, CustomerAddMoneySchema
from Services.GenericCRUDServices import GenericUpdater
from Services.JWTTokenServices import GenerateJWTTokenFromExistingSession
from Services.ActivityServices import AddActivityLog
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError
from Services.CommonServices import   GetCurrentActiveSession, GetErrorMessage
from Services.CBSServices import IsAccountrValid
from Services.StripeServices import InitializeStripPaymentSession
from sqlalchemy.ext.asyncio import AsyncSession
from Config.dbConnection import AsyncSessionLocalClickNet
from Models.shared import customerUserProfile, customerAddMoney

AddMoneyRoutes = APIRouter(prefix="/AddMoney")

@AddMoneyRoutes.post("/InitializeAddMoney")
async def InitializeAddMoney(data:AddMoneyViewModelSchema, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        if not await IsAccountrValid(data.ToAccountNo, currentCustuserprofile.customer_id):
            raise ValueError(f"Account number '{data.ToAccountNo}' does not belong to the logged-in customer.")
        
        if data.Vendor.upper() == "STRIPE":
            status = await _InitializeAddMoneyFromStripe(data, currentCustuserprofile)
        else:
            raise ValueError("Invalid vendor for add money.")
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AddMoneyRoutes/InitializeAddMoney",
            CreatedBy=""
        ))
    return status


@AddMoneyRoutes.get("/ProcessAddMoneyCallback")
async def ProcessAddMoneyCallback(secret_key:str)-> StatusResult:
    status = StatusResult()
    try:
        status = await _ProcessCallback(secret_key)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AddMoneyRoutes/ProcessAddMoneyCallback",
            CreatedBy=""
        ))
    return status


async def _InitializeAddMoneyFromStripe(data:AddMoneyViewModelSchema, currentCustuserprofile:CustomerUserProfileSchema)-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.FUNDTRANSFER,
            Title="Trying to add money from Stripe",
            Details=f"{currentCustuserprofile.user_id.lower()} is trying to add money from Stripe to {data.ToAccountNo}",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
        
        
        payment_id = await InitializeStripPaymentSession(data, currentCustuserprofile)
        if payment_id:
            status.Status = "OK"
            status.Message = None
            status.Result = payment_id
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.FUNDTRANSFER,
                Title="Successfully initialized payment from Strip",
                Details=f"{currentCustuserprofile.user_id.lower()} is successfully initialized payment from Strip to {data.ToAccountNo}",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))

        else:
            raise ValueError("Failed due to internal error.")
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AddMoneyRoutes/_AddMoneyFromStripe",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.FUNDTRANSFER,
            Title="Failed to initialize payment from Strip",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to initialize payment from Strip to {data.ToAccountNo}. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

async def _ProcessCallback(secret_key:str) -> StatusResult:
    status = StatusResult()
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(
            select(customerAddMoney).where(
                or_(
                    customerAddMoney.c.SUCCESS_SECRET_KEY == secret_key,
                    customerAddMoney.c.FAILED_SECRET_KEY == secret_key
                )
            )
        )
        if result is not None:
            row = result.fetchone()
            
        if row:
            addmoney = CustomerAddMoneySchema(**dict(row._mapping))
        if addmoney:
            paymentStatus = None
            if addmoney.success_secret_key == secret_key:
                paymentStatus="Success"
            elif addmoney.failed_secret_key == secret_key:
                paymentStatus="Failed"
            else:
                raise ValueError("Invalid secret key.")
            
            addmoney.success_or_failed_process_dt = datetime.now()
            await GenericUpdater.update_record(
                table=customerAddMoney,
                schema_model=CustomerAddMoneySchema,
                record_id=addmoney.id,
                update_data=addmoney,
                id_column="ID",
                exclude_fields={}
            )
            session = await GetCurrentActiveSession(addmoney.user_id)

            if not session:
                raise ValueError("Session Expired. Please Login again")
            
            access_token = await GenerateJWTTokenFromExistingSession(session)
            
            if access_token:
                decoded_token = jwt.decode(access_token, options={"verify_signature": False})
                start_date = decoded_token.get("StartDate")
                expiry_date = decoded_token.get("ExpiryDate")

                result = await db_session.execute(
                    select(customerUserProfile)
                    .where(func.lower(customerUserProfile.c.USER_ID) == addmoney.user_id.lower())
                )
                if result is not None:
                    row = result.fetchone()
                
                user_profile = CustomerUserProfileSchema(**dict(row._mapping))
                
                if user_profile:
                    transectionData = {
                        "ToAccountNo":addmoney.receiver_no,
                        "ReceiverName":addmoney.receiver_name,
                        "Amount":(addmoney.amount_in_cent/100),
                        "Currency":addmoney.currency,
                        "Vendor":addmoney.payment_via,
                        "ReferenceId":addmoney.payment_id
                    }
                    
                    login_model = {
                        "access_token": access_token,
                        "token_type": "Bearer",
                        "expires_in": int((datetime.fromisoformat(expiry_date) - datetime.fromisoformat(start_date)).total_seconds() * 1000),
                        "userName": user_profile.user_id,
                        "fullName": user_profile.user_nm,
                        "issued": start_date,
                        "expires": expiry_date,
                        "customerId": user_profile.customer_id,
                        "ForcePasswordChangedFlag": user_profile.force_password_changed_flag
                    }
                    
                    response_model = {
                        "PaymentStatus":paymentStatus,
                        "LoginData": login_model,
                        "TransactionData":transectionData                        
                    } 
                    
                    status.Status = "OK"
                    status.Message = ""
                    status.Result = response_model
                    return status
                else:
                    raise ValueError("Invalid data for user-")
            
        else:
            raise ValueError("Invalid secret key.")

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AddMoneyRoutes/_ProcessCallback",
            CreatedBy=""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        return status
    finally:
        if db_session:
            await db_session.close()
