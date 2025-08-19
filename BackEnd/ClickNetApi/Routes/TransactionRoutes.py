import json
import os
import traceback
from fastapi import APIRouter, Depends
from kafka import KafkaProducer
from Schemas.Enums.Enums import ActivityType
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema, FundTransferViewModelSchema, CustomerOtpSchema, CustomerUserProfileSchema
from Services.ActivityServices import AddActivityLog
from Cache.AppSettingsCache import Get
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError
from Services.CommonServices import  GetDecryptedText, GetCurrentActiveSession, GetErrorMessage
from Services.CBSServices import CBSFundTransfer, GetTrasactionLimitInfoByAccountNo, IsAccountrValid
from Services.OTPServices import Authentication

TransactionRoutes = APIRouter(prefix="/Transaction")

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks='all'
)

@TransactionRoutes.post("/Fundtransfer")
async def Fundtransfer(data:FundTransferViewModelSchema, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.FUNDTRANSFER,
            Title="Trying to transfer fund",
            Details=f"{currentCustuserprofile.user_id.lower()} is trying to transfer fund from {data.FromAccount} to {data.ToAccount}",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))

        # Fetch sender's account transaction limit info
        acc_limit_info = await GetTrasactionLimitInfoByAccountNo(data.FromAccount)

        # Validation
        if acc_limit_info.payment_frequency not in ("D", "M"):
            raise ValueError("Unsupported payment frequency.")

        if float(data.Amount) < acc_limit_info.payment_min_amount:
            raise ValueError(f"Transfer amount {float(data.Amount)} is below minimum allowed: {acc_limit_info.payment_min_amount}")

        if (acc_limit_info.today_total_amount or 0) + float(data.Amount) > acc_limit_info.payment_max_amount:
            raise ValueError(
                f"Transfer exceeds daily limit. Current total + new = {(acc_limit_info.today_total_amount or 0) + float(data.Amount)}, max = {acc_limit_info.payment_max_amount}"
            )

        if (acc_limit_info.today_total_transactions or 0) >= acc_limit_info.daily_no_of_payments:
            raise ValueError(
                f"Exceeded allowed number of daily transfers. Today's count = {acc_limit_info.today_total_transactions}, allowed = {acc_limit_info.daily_no_of_payments}"
            )
        
        if not await IsAccountrValid(data.FromAccount, currentCustuserprofile.customer_id):
            raise ValueError(f"Account number '{data.FromAccount}' does not belong to the logged-in customer.")
        
        # OTP/TPIN verification
        status = await Authentication(CustomerOtpSchema(
            user_id=currentCustuserprofile.user_id.lower(),
            cust_id=currentCustuserprofile.customer_id,
            phone_number=await GetDecryptedText(currentCustuserprofile.mobile_number),
            email_address=await GetDecryptedText(currentCustuserprofile.email_address),
            verification_channel=data.OTP_verify_channel,
            from_account_no=data.FromAccount,
            to_account_no=data.ToAccount,
            ip_address="",
            amount_ccy=float(data.Amount),
            amount_lcy=float(data.Amount),
            transfer_type="TRANSFER",
            purpose_of_transaction=data.Pourpose,
            receiver_nm=data.ReceiverName,
            otp=data.OTP
        ))
        
        if  status.Status.upper() != "OK":
            return status
        
        trans_id = await CBSFundTransfer(data)
        if trans_id:
            await _SendFtNotification(currentCustuserprofile, data, trans_id)
            
            status.Status = "OK"
            status.Message = f"{float(data.Amount)} {data.Currency} is successfully transfered from {data.FromAccount}. TXID : {trans_id}"
            status.Result = trans_id
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.FUNDTRANSFER,
                Title="Successfully transfered fund",
                Details=f"{currentCustuserprofile.user_id.lower()} is successfully transfered from {data.FromAccount} to {data.ToAccount}",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))

        else:
            raise ValueError("Transaction failed due to internal error.")
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="TransactionRoutes/Fundtransfer",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.FUNDTRANSFER,
            Title="Failed to transfer fund",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to transfer fund from {data.FromAccount} to {data.ToAccount}. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status
    

async def _SendFtNotification(data:CustomerUserProfileSchema, ftData:FundTransferViewModelSchema, trx_id:str) -> bool:
    try:
        is_credential_sent = False

        registered_email = (await GetDecryptedText(data.email_address)).strip().lower()
        registered_mobile = (await GetDecryptedText(data.mobile_number)).strip()

        SendMethod = Get("CREDENTIALS_SENDING_PROCESS")
        
        sms_body = Get(f"SMS_USER_FUND_TRANSFER_BODY")
        sms_body = sms_body.replace("_userId_", data.user_id.lower()) \
                .replace("_amount_", ftData.Amount) \
                .replace("_currency_", ftData.Currency.upper()) \
                .replace("_fromAccount_", ftData.FromAccount) \
                .replace("_toAccount_", ftData.ToAccount) \
                .replace("_transactionId_", trx_id) \
                .replace("_purpose_", ftData.Pourpose)
        
        email_body = Get(f"EMAIL_USER_FUND_TRANSFER_BODY")
        email_body = email_body.replace("_userId_", data.user_id.lower()) \
                .replace("_amount_", ftData.Amount) \
                .replace("_currency_", ftData.Currency.upper()) \
                .replace("_fromAccount_", ftData.FromAccount) \
                .replace("_toAccount_", ftData.ToAccount) \
                .replace("_transactionId_", trx_id) \
                .replace("_purpose_", ftData.Pourpose)      
                
        kafkaAck = producer.send(
                "send_notification",
                value={
                    "delivery_channel": SendMethod,
                    "phone": registered_mobile,
                    "email": registered_email,
                    "title": "Payment confirmation",
                    "sms_message": sms_body,
                    "email_message": email_body
                }
            )
        try:
            kafkaAck.get(timeout=10) 
            is_credential_sent = True
        except Exception as kafka_ex:
            raise RuntimeError(f"Failed to send message to Kafka: {str(kafka_ex)}")

        return is_credential_sent
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg = error_msg,
            Type = "ERROR",
            ModuleName = "TransactionRoutes/_SendFtNotification",
            CreatedBy = ""
        ))
        return False
