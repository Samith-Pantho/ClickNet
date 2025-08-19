from datetime import datetime
import traceback
from fastapi import APIRouter, Depends, Request
import jwt
from Schemas.shared import StatusResult, SystemLogErrorSchema, InitializeRequestviewModelShema, VerifiyEmailRequestviewModelShema, VerifiyMobileRequestviewModelShema
from Services.CBSServices import CheckCustomerForProduct, GetBranchList, GetCustomerbyID, GetProductsForKyc, CreateAccount, CreateCustomer
from Services.CommonServices import GetErrorMessage, SendCredentials
from Services.DigitServices import CreateDiditSession
from Services.JWTTokenServices import GenerateJWTToken, ValidateJWTToken
from Services.KYCServices import GetTrackingData, InitializeTrackingId, UpdateTrackingData
from Services.LogServices import AddLogOrError
from Services.OTPServices import CheckEmailOTPforVerification, CheckMobileOTPforVerification, SendOTPforEmailVerification, SendOTPforMobileVerification
from Services.ReportServices import GenerateCustomerProfile

InternalRoutes = APIRouter(prefix="/Internal")

@InternalRoutes.get("/GetProductList/{product_catagory}")
async def GetProductList(product_catagory:str):
    status = StatusResult()
    try:
        products = await GetProductsForKyc(product_catagory)

        if products is not None:
            status.Status = "OK"
            status.Message = ""
            status.Result = products
        else:
            raise ValueError("No data found.")
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/GetProductList",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None

    return status

@InternalRoutes.get("/GetBranches")
async def GetBranches():
    status = StatusResult()
    try:
        branches = await GetBranchList()

        if branches is not None:
            status.Status = "OK"
            status.Message = ""
            status.Result = branches
        else:
            raise ValueError("No data found.")
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/GetBranchList",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None

    return status

@InternalRoutes.get("/SendOTPforMobile/{phone_number}")
async def SendOTPforMobile(phone_number:str):
    status = StatusResult()
    try:
        status = await SendOTPforMobileVerification(phone_number)
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/SendOTPforMobile",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status

@InternalRoutes.post("/CheckMobileOTP")
async def CheckMobileOTP(data: VerifiyMobileRequestviewModelShema):
    status = StatusResult()
    try:
        status = await CheckMobileOTPforVerification(data)
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/CheckMobileOTP",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status

@InternalRoutes.get("/SendOTPforEmail/{email_address}")
async def SendOTPforEmail(email_address:str):
    status = StatusResult()
    try:
        status = await SendOTPforEmailVerification(email_address)
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/SendOTPforEmail",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status

@InternalRoutes.post("/CheckEmailOTP")
async def CheckEmailOTP(data:VerifiyEmailRequestviewModelShema):
    status = StatusResult()
    try:
        status = await CheckEmailOTPforVerification(data)
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/CheckEmailOTP",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status

@InternalRoutes.post("/Initialize")
async def Initialize(data:InitializeRequestviewModelShema):
    status = StatusResult()
    try:
        tracking_id = await InitializeTrackingId(data.phone_number, data.product_code)
        if tracking_id:
            customerRegistrationData = await GetTrackingData(tracking_id)
            if customerRegistrationData.status == "PROCESSED":
                raise ValueError("You already have an account associated with this product.")
            
            customerRegistrationData.branch_code = data.branch_code
            customerRegistrationData.email_address = data.email_address
            
            result = await UpdateTrackingData(customerRegistrationData)
            print(result)
            if result == "PROCESSED":
                raise ValueError("No further action is required, as this entry has already been processed.")
            elif result == "REJECTED":
                raise ValueError("This record has already been marked as rejected; no further updates are permitted.")
            else:
                access_token = await GenerateJWTToken(tracking_id)
                if access_token:
                    decoded_token = jwt.decode(access_token, options={"verify_signature": False})
                    start_date = decoded_token.get("StartDate")
                    expiry_date = decoded_token.get("ExpiryDate")
                    
                    customerRegistrationData = await GetTrackingData(tracking_id)
                    
                    response_model = {
                        "access_token":access_token,
                        "token_type": "Bearer",
                        "expires_in": int((datetime.fromisoformat(expiry_date) - datetime.fromisoformat(start_date)).total_seconds() * 1000),
                        "customer_data" : customerRegistrationData
                    }
                
                    status.Status = "OK"
                    status.Message = "Initialized"
                    status.Result = response_model
                else:
                    raise ValueError("Failed to create access token.")
        else:
            raise ValueError("Failed to create tracking id.")
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/InitializeTrackingId",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None

    return status

@InternalRoutes.get("/Initializeverification")
async def Initializeverification(existingCustomerData=Depends(ValidateJWTToken)):
    status = StatusResult()
    try:
        status = await CreateDiditSession(existingCustomerData.tracking_id)
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/Initializeverification",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status

@InternalRoutes.get("/GetCustomerRegistrationData")
async def GetCustomerRegistrationData(existingCustomerData=Depends(ValidateJWTToken)):
    status = StatusResult()
    try:
        if existingCustomerData.tax_id and existingCustomerData.product_code:
            customer_id = await CheckCustomerForProduct(existingCustomerData.tax_id, existingCustomerData.product_code)
            if customer_id != "":
                existingCustomerData.status = "REJECTED"
                if existingCustomerData.reject_reason:
                    existingCustomerData.reject_reason = f"{existingCustomerData.reject_reason}\nDuplicate check failed: an account of the same product already exists."
                else:
                    existingCustomerData.reject_reason = "Duplicate check failed: an account of the same product already exists."
                result = await UpdateTrackingData(existingCustomerData)
                
            CustomerData = await GetTrackingData(existingCustomerData.tracking_id)
            status.Status = "OK"
            status.Message = None
            status.Result = CustomerData
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/GetCustomerRegistrationData",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status

@InternalRoutes.get("/CreateCustomerAndAccount")
async def CreateCustomerAndAccount(existingCustomerData=Depends(ValidateJWTToken)):
    status = StatusResult()
    try:
        existingCustomerData.customer_id = await GetCustomerbyID(existingCustomerData.tax_id)                
            
        if not existingCustomerData.customer_id and not existingCustomerData.account_number:
            existingCustomerData = await CreateCustomer(existingCustomerData)
        
        if existingCustomerData.customer_id and not existingCustomerData.account_number:
            existingCustomerData = await CreateAccount(existingCustomerData)
        
        if existingCustomerData.customer_id and existingCustomerData.account_number:
            result = await UpdateTrackingData(existingCustomerData)
            if result == "REJECTED":
                raise ValueError("This record has already been marked as rejected; no further updates are permitted.")
            else:
                CustomerData = await GetTrackingData(existingCustomerData.tracking_id)
                status = await SendCredentials(CustomerData)
                status.Message = f"Account created successfully. {status.Message}" 
                status.Result = CustomerData
                return status
        else:
              if not existingCustomerData.customer_id:
                  raise ValueError("Customer Id creation failed.")
              elif not existingCustomerData.account_number:
                  raise ValueError("Account No creation failed.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/CreateCustomerAndAccount",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        return status

@InternalRoutes.get("/GenerateReport")
async def GenerateReport(existingCustomerData=Depends(ValidateJWTToken)):
    status = StatusResult()
    try:
        report = await GenerateCustomerProfile(existingCustomerData)
        status.Status = "OK"
        status.Message = None
        status.Result = report
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "InternalRoutes/GenerateReport",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
    return status
