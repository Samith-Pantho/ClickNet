from Config.dbConnection import engine 
from .LogServices import AddLogOrError

from Schemas.shared import SystemLogErrorSchema, CBSCustomerInfoSchema, CBSCustomerAccountsSchema, CBSAccountDetailsSchema, CBSAccountFullDetailsSchema, CBSAccountBalanceDetailsSchema, CBSCustomerAddressSchema, CBSCustomerEmailSchema, CBSCustomerPhoneSchema, CBSCustomerFullInfoSchema, CBSAccountWiseTransLimitInfoSchema

from .CallCBSSPServices import sp_get_customer_info, sp_get_customer_addresses, sp_get_customer_emails, sp_get_customer_phones, sp_get_customer_accounts, sp_get_customer_accounts_with_details, sp_get_account_info, sp_get_account_balances_and_rate, sp_get_available_balance, sp_get_account_wise_trans_limit_info

def GetCustomerInfo(customer_id:str) -> CBSCustomerInfoSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_customer_info(_conn, customer_id)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerInfo",
            CreatedBy = ""
        ))
        return None

def GetCustomerAddresses(customer_id:str) -> CBSCustomerAddressSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_customer_addresses(_conn, customer_id)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerAddresses",
            CreatedBy = ""
        ))
        return None

def GetCustomerEmails(customer_id:str) -> CBSCustomerEmailSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_customer_emails(_conn, customer_id)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerEmails",
            CreatedBy = ""
        ))
        return None

def GetCustomerPhones(customer_id:str) -> CBSCustomerPhoneSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_customer_phones(_conn, customer_id)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerPhones",
            CreatedBy = ""
        ))
        return None

def GetCustomerFullInformation(customer_id:str) -> CBSCustomerFullInfoSchema:
    try:
        with engine.connect() as _conn:
            return CBSCustomerFullInfoSchema(
                customer=sp_get_customer_info(_conn, customer_id),
                addresses=sp_get_customer_addresses(_conn, customer_id),
                emails=sp_get_customer_emails(_conn, customer_id),
                phones=sp_get_customer_phones(_conn, customer_id)
            )
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerFullInformation",
            CreatedBy = ""
        ))
        return None

def GetCustomerAccounts(customer_id:str, product_category:str) -> CBSCustomerAccountsSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_customer_accounts(_conn, customer_id, product_category)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerAccounts",
            CreatedBy = ""
        ))
        return None

def GetCustomerAccountsWithDetails(customer_id:str, product_category:str) -> CBSAccountFullDetailsSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_customer_accounts_with_details(_conn, customer_id, product_category)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerAccountsWithDetails",
            CreatedBy = ""
        ))
        return None

def GetAccountDetailsByAccountNo(account_number:str) -> CBSAccountDetailsSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_account_info(_conn, account_number)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetAccountDetailsByAccountNo",
            CreatedBy = ""
        ))
        return None

def GetBalancesAndRateByAccountNo(account_number:str) -> CBSAccountBalanceDetailsSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_account_balances_and_rate(_conn, account_number)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetBalancesAndRateByAccountNo",
            CreatedBy = ""
        ))
        return None

def GetAvailableBalanceByAccountNo(account_number:str) -> float:
    try:
        with engine.connect() as _conn:
            return sp_get_available_balance(_conn, account_number)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetAvailableBalanceByAccountNo",
            CreatedBy = ""
        ))
        return None

def GetTrasactionLimitInfoByAccountNo(account_number:str) -> CBSAccountWiseTransLimitInfoSchema:
    try:
        with engine.connect() as _conn:
            return sp_get_account_wise_trans_limit_info(_conn, account_number)
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CBSServices/GetTrasactionLimitInfoByAccountNo",
            CreatedBy = ""
        ))
        return None
