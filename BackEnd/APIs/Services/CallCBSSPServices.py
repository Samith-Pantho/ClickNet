import json
from sqlalchemy import text
from .LogServices import AddLogOrError
from Schemas.shared import SystemLogErrorSchema, CBSCustomerInfoSchema, CBSCustomerAccountsSchema, CBSAccountDetailsSchema, CBSAccountFullDetailsSchema, CBSAccountBalanceDetailsSchema, CBSCustomerAddressSchema, CBSCustomerEmailSchema, CBSCustomerPhoneSchema, CBSAccountWiseTransLimitInfoSchema

# 1. Fetch customer info by customer_id
def sp_get_customer_info(conn, customer_id):
    try:
        sql = text("CALL CBS_GetCustomerInfo(:p_customer_id)")
        result = conn.execute(sql, {"p_customer_id": customer_id})
        row = result.fetchone()
        return CBSCustomerInfoSchema(**dict(row._mapping)) if row else None
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_info",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 2. Fetch customer addresses by customer_id
def sp_get_customer_addresses(conn, customer_id):
    try:
        sql = text("CALL CBS_GetCustomerAddresses(:p_customer_id)")
        result = conn.execute(sql, {"p_customer_id": customer_id})
        return [CBSCustomerAddressSchema(**dict(row._mapping)) for row in result.fetchall()]
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_addresses",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 3. Fetch customer emails by customer_id
def sp_get_customer_emails(conn, customer_id):
    try:
        sql = text("CALL CBS_GetCustomerEmails(:p_customer_id)")
        result = conn.execute(sql, {"p_customer_id": customer_id})
        return [CBSCustomerEmailSchema(**dict(row._mapping)) for row in result.fetchall()]
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_emails",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 4. Fetch customer phones by customer_id
def sp_get_customer_phones(conn, customer_id):
    try:
        sql = text("CALL CBS_GetCustomerPhones(:p_customer_id)")
        result = conn.execute(sql, {"p_customer_id": customer_id})
        return [CBSCustomerPhoneSchema(**dict(row._mapping)) for row in result.fetchall()]
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_phones",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 5. Fetch customer accounts with details by customer_id and product_category
def sp_get_customer_accounts_with_details(conn, customer_id, product_category=None):
    try:
        sql = text("CALL CBS_GetCustomerAccountsWithDetails(:p_customer_id, :p_product_category)")
        pc = product_category if product_category else ""
        result = conn.execute(sql, {"p_customer_id": customer_id, "p_product_category": pc})
        return [CBSAccountFullDetailsSchema(**dict(row._mapping)) for row in result.fetchall()]
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_accounts_with_details",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 6. Fetch customer accounts by customer_id and product_category
def sp_get_customer_accounts(conn, customer_id, product_category=None):
    try:
        sql = text("CALL CBS_GetCustomerAccounts(:p_customer_id, :p_product_category)")
        pc = product_category if product_category else ""
        result = conn.execute(sql, {"p_customer_id": customer_id, "p_product_category": pc})
        return [CBSCustomerAccountsSchema(**dict(row._mapping)) for row in result.fetchall()]
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_accounts",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 7. Fetch account info by account_number
def sp_get_account_info(conn, account_number):
    try:
        sql = text("CALL CBS_GetAccountInfo(:p_account_number)")
        result = conn.execute(sql, {"p_account_number": account_number})
        row = result.fetchone()
        return CBSAccountDetailsSchema(**dict(row._mapping)) if row else None
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_account_info",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 8. Fetch balances and interest rate by account_number
def sp_get_account_balances_and_rate(conn, account_number):
    try:
        sql = text("CALL CBS_GetAccountBalancesAndRate(:p_account_number)")
        result = conn.execute(sql, {"p_account_number": account_number})
        row = result.fetchone()
        return CBSAccountBalanceDetailsSchema(**dict(row._mapping)) if row else None
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_account_balances_and_rate",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 9. Fetch only available balance by account_number
def sp_get_available_balance(conn, account_number):
    try:
        sql = text("CALL CBS_GetAvailableBalance(:p_account_number)")
        result = conn.execute(sql, {"p_account_number": account_number})
        row = result.fetchone()
        if row:
            row_dict = dict(row._mapping)
            return float(row_dict.get("available_balance", "0"))
        else:
            return 0.0
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_available_balance",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 10. Fetch Account Wise Trans Limit info by account_number
def sp_get_account_wise_trans_limit_info(conn, account_number):
    try:
        sql = text("CALL CBS_GetAccountWiseTransLimitInfo(:p_account_number)")
        result = conn.execute(sql, {"p_account_number": account_number})
        row = result.fetchone()
        return CBSAccountWiseTransLimitInfoSchema(**dict(row._mapping)) if row else None
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_account_wise_trans_limit_info",
            CreatedBy = ""
        ))
        raise Exception(ex)
