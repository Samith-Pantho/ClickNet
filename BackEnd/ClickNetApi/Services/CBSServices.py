from datetime import datetime
import traceback
from Config.dbConnection import AsyncSessionLocalCBS
from sqlalchemy.ext.asyncio import AsyncSession
from .LogServices import AddLogOrError

from Schemas.shared import SystemLogErrorSchema, CBSCustomerInfoSchema, CBSCustomerAccountsSchema, CBSAccountDetailsSchema, CBSAccountFullDetailsSchema, CBSAccountBalanceDetailsSchema, CBSCustomerAddressSchema, CBSCustomerEmailSchema, CBSCustomerPhoneSchema, CBSCustomerFullInfoSchema, CBSAccountWiseTransLimitInfoSchema, FundTransferViewModelSchema, CBSTransactionHistorySchema

from .CallCBSSPServices import sp_fund_transfer, sp_get_account_transaction_history, sp_get_branch_list_with_details, sp_get_customer_info, sp_get_customer_addresses, sp_get_customer_emails, sp_get_customer_phones, sp_get_customer_accounts, sp_get_customer_accounts_with_details, sp_get_account_info, sp_get_account_balances_and_rate, sp_get_available_balance, sp_get_account_wise_trans_limit_info

async def GetCustomerInfo(customer_id:str) -> CBSCustomerInfoSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_customer_info(db_session, customer_id)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerInfo",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetCustomerAddresses(customer_id:str) -> CBSCustomerAddressSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_customer_addresses(db_session, customer_id)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerAddresses",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetCustomerEmails(customer_id:str) -> CBSCustomerEmailSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_customer_emails(db_session, customer_id)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerEmails",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetCustomerPhones(customer_id:str) -> CBSCustomerPhoneSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_customer_phones(db_session, customer_id)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerPhones",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetCustomerFullInformation(customer_id:str) -> CBSCustomerFullInfoSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return CBSCustomerFullInfoSchema(
                customer=await sp_get_customer_info(db_session, customer_id),
                addresses=await sp_get_customer_addresses(db_session, customer_id),
                emails=await sp_get_customer_emails(db_session, customer_id),
                phones=await sp_get_customer_phones(db_session, customer_id)
            )
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerFullInformation",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetCustomerAccounts(customer_id:str, product_category:str) -> CBSCustomerAccountsSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_customer_accounts(db_session, customer_id, product_category)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerAccounts",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetCustomerAccountsWithDetails(customer_id:str, product_category:str) -> CBSAccountFullDetailsSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_customer_accounts_with_details(db_session, customer_id, product_category)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerAccountsWithDetails",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetAccountDetailsByAccountNo(account_number:str) -> CBSAccountDetailsSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_account_info(db_session, account_number)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetAccountDetailsByAccountNo",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetBalancesAndRateByAccountNo(account_number:str) -> CBSAccountBalanceDetailsSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_account_balances_and_rate(db_session, account_number)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetBalancesAndRateByAccountNo",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetAvailableBalanceByAccountNo(account_number:str) -> float:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_available_balance(db_session, account_number)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetAvailableBalanceByAccountNo",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetTrasactionLimitInfoByAccountNo(account_number:str) -> CBSAccountWiseTransLimitInfoSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_account_wise_trans_limit_info(db_session, account_number)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetTrasactionLimitInfoByAccountNo",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def CBSFundTransfer(data:FundTransferViewModelSchema) -> str:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_fund_transfer(db_session, data)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/CBSFundTransfer",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def GetAccountWiseTransactionHistory(account_number:str, start_date: datetime, end_date: datetime, sort_direction:str) -> CBSTransactionHistorySchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_account_transaction_history(db_session, account_number, start_date, end_date, sort_direction)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetAccountWiseTransactionHistory",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def IsAccountrValid(account_number: str, customer_id: str) -> bool:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        allAccounts = await sp_get_customer_accounts(db_session, customer_id, None)

        if allAccounts:
            return any(acc.account_number == account_number for acc in allAccounts)
        return False

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CBSServices/IsAccountrValid",
            CreatedBy=""
        ))
        return False
    finally:
        if db_session:
            await db_session.close()
            
async def GetBranchList():
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_branch_list_with_details(db_session)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetBranchList",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()