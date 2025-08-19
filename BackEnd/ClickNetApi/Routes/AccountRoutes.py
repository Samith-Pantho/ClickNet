from datetime import datetime
import traceback
from typing import Optional
from fastapi import APIRouter, Depends
from datetime import datetime
from Schemas.Enums.Enums import ActivityType
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema
from Services.ActivityServices import AddActivityLog
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError
from Services.CommonServices import   GetCurrentActiveSession, GetErrorMessage
from Services.CBSServices import IsAccountrValid, GetAccountWiseTransactionHistory, GetCustomerAccounts, GetCustomerAccountsWithDetails, GetAccountDetailsByAccountNo, GetBalancesAndRateByAccountNo, GetAvailableBalanceByAccountNo, GetTrasactionLimitInfoByAccountNo
from Services.ReportServices import GenerateStatement

AccountRoutes = APIRouter(prefix="/Account")

@AccountRoutes.get("/FetchAllAccounts")
async def FetchAllAccounts(product_category: Optional[str] = None, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        allAccounts = await GetCustomerAccounts(currentCustuserprofile.customer_id, product_category)
        if allAccounts:
            status.Status = "OK"
            status.Message = "Successfully fetched all accounts"
            status.Result = allAccounts
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.ACCOUNT,
                Title="Successfully fetched all accounts",
                Details=f"{currentCustuserprofile.user_id.lower()} is successfully fetched all accounts.",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AccountRoutes/FetchAllAccounts",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.ACCOUNT,
            Title="Failed to fetch all accounts",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch all accounts. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

@AccountRoutes.get("/FetchAllAccountsWithDetails")
async def FetchAllAccountsWithDetails(product_category: Optional[str] = None, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        allAccounts = await GetCustomerAccountsWithDetails(currentCustuserprofile.customer_id, product_category)
        if allAccounts:
            status.Status = "OK"
            status.Message = "Successfully fetched all accounts with details"
            status.Result = allAccounts
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.ACCOUNT,
                Title="Successfully fetched all accounts",
                Details=f"{currentCustuserprofile.user_id.lower()} is successfully fetched all accounts with details.",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AccountRoutes/FetchAllAccountsWithDetails",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.ACCOUNT,
            Title="Failed to fetch all accounts",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch all accounts with details. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

@AccountRoutes.get("/FetchAccountDetailsByAccountNo")
async def FetchAccountDetailsByAccountNo(account_number:str, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        if not await IsAccountrValid(account_number, currentCustuserprofile.customer_id):
            raise ValueError(f"Account number '{account_number}' does not belong to the logged-in customer.")
        
        accountDetails = await GetAccountDetailsByAccountNo(account_number)
        if accountDetails:
            status.Status = "OK"
            status.Message = "Successfully fetched account details"
            status.Result = accountDetails
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.ACCOUNT,
                Title="Successfully fetched account details",
                Details=f"{currentCustuserprofile.user_id.lower()} is successfully fetched account details.",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AccountRoutes/FetchAccountDetailsByAccountNo",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.ACCOUNT,
            Title="Failed to fetch account details",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch account details. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

@AccountRoutes.get("/FetchBalancesAndRateByAccountNo")
async def FetchBalancesAndRateByAccountNo(account_number:str, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        if not await IsAccountrValid(account_number, currentCustuserprofile.customer_id):
            raise ValueError(f"Account number '{account_number}' does not belong to the logged-in customer.")
        
        balancesAndrate = await GetBalancesAndRateByAccountNo(account_number)
        if balancesAndrate:
            status.Status = "OK"
            status.Message = "Successfully fetched balances and rates of account"
            status.Result = balancesAndrate
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.ACCOUNT,
                Title="Successfully fetched balances and rates of account",
                Details=f"{currentCustuserprofile.user_id.lower()} is Successfully fetched balances and rates of account.",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AccountRoutes/FetchBalancesAndRateByAccountNo",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.ACCOUNT,
            Title="Failed to fetch balances and rates of account",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch balances and rates of account. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

@AccountRoutes.get("/FetchAvailableBalanceByAccountNo")
async def FetchAvailableBalanceByAccountNo(account_number:str, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        if not await IsAccountrValid(account_number, currentCustuserprofile.customer_id):
            raise ValueError(f"Account number '{account_number}' does not belong to the logged-in customer.")
        
        availableBalance = await GetAvailableBalanceByAccountNo(account_number)
        if availableBalance:
            status.Status = "OK"
            status.Message = "Successfully fetched available balance of account"
            status.Result = availableBalance
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.ACCOUNT,
                Title="Successfully fetched available balance of account",
                Details=f"{currentCustuserprofile.user_id.lower()} is Successfully fetched available balance of account.",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AccountRoutes/FetchAvailableBalanceByAccountNo",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.ACCOUNT,
            Title="Failed to fetch available balance of account",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch available balance of account. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

@AccountRoutes.get("/FetchTrasactionLimitInfoByAccountNo")
async def FetchTrasactionLimitInfoByAccountNo(account_number:str, currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        if not await IsAccountrValid(account_number, currentCustuserprofile.customer_id):
            raise ValueError(f"Account number '{account_number}' does not belong to the logged-in customer.")
        
        transLimit = await GetTrasactionLimitInfoByAccountNo(account_number)
        if transLimit:
            status.Status = "OK"
            status.Message = "Successfully fetched transaction limit info of account"
            status.Result = transLimit
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.ACCOUNT,
                Title="Successfully fetched transaction limit info of account",
                Details=f"{currentCustuserprofile.user_id.lower()} is Successfully fetched transaction limit info of account.",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AccountRoutes/FetchTrasactionLimitInfoByAccountNo",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.ACCOUNT,
            Title="Failed to fetch transaction limit info of account",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch transaction limit info of account. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

@AccountRoutes.get("/FetchAccountWiseTransactionHistory")
async def FetchAccountWiseTransactionHistory(account_number:str, start_date: Optional[datetime], end_date: Optional[datetime], currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        if not await IsAccountrValid(account_number, currentCustuserprofile.customer_id):
            raise ValueError(f"Account number '{account_number}' does not belong to the logged-in customer.")
        
        if not start_date and not end_date:
            start_date = end_date = datetime.today()
        elif not start_date:
            start_date = end_date
        elif not end_date:
            end_date = start_date
        
        transHist = await GetAccountWiseTransactionHistory(account_number, start_date, end_date, "DESC")
        if transHist:
            status.Status = "OK"
            status.Message = "Successfully fetched transaction history"
            status.Result = transHist
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.ACCOUNT,
                Title="Successfully fetched transaction history",
                Details=f"{currentCustuserprofile.user_id.lower()} is Successfully fetched transaction history.",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AccountRoutes/FetchAccountWiseTransactionHistory",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.ACCOUNT,
            Title="Failed to fetch transaction history",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch transaction history. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

@AccountRoutes.get("/GenerateStatementOfAccount")
async def GenerateStatementOfAccount(account_number:str, start_date: Optional[datetime], end_date: Optional[datetime], currentCustuserprofile=Depends(ValidateJWTToken))-> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        if not await IsAccountrValid(account_number, currentCustuserprofile.customer_id):
            raise ValueError(f"Account number '{account_number}' does not belong to the logged-in customer.")
        
        
        if not start_date and not end_date:
            start_date = end_date = datetime.today()
        elif not start_date:
            start_date = end_date
        elif not end_date:
            end_date = start_date
        
        transHist = await GetAccountWiseTransactionHistory(account_number, start_date, end_date, "ASC")
        balancesAndrate = await GetBalancesAndRateByAccountNo(account_number)
        
        if transHist:
            statementBase64 = await GenerateStatement(transHist, account_number, currentCustuserprofile.user_nm, balancesAndrate.original_balance, balancesAndrate.current_balance, "USD")
            if statementBase64:
                status.Status = "OK"
                status.Message = "Successfully generated statement"
                status.Result = statementBase64
                
                await AddActivityLog(SystemActivitySchema(
                    Type=ActivityType.ACCOUNT,
                    Title="Successfully generated statement",
                    Details=f"{currentCustuserprofile.user_id.lower()} is Successfully generated statement of {account_number}.",
                    IpAddress=session.ip_address if session else "",
                    UserType="USER",
                    User_Id=currentCustuserprofile.user_id.lower()
                ))
        else:
            raise ValueError("No data found.")
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="AccountRoutes/GenerateStatementOfAccount",
            CreatedBy=""
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.ACCOUNT,
            Title="Failed to generate statement",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to generate statement of {account_number}. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status
