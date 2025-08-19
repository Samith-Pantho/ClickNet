import json
import traceback
from sqlalchemy import text
from .LogServices import AddLogOrError
from Schemas.shared import SystemLogErrorSchema, CBSCustomerInfoSchema, CBSCustomerAccountsSchema, CBSAccountDetailsSchema, CBSAccountFullDetailsSchema, CBSAccountBalanceDetailsSchema, CBSCustomerAddressSchema, CBSCustomerEmailSchema, CBSCustomerPhoneSchema, CBSAccountWiseTransLimitInfoSchema, FundTransferViewModelSchema, CBSTransactionHistorySchema, CBSBranchDetailsSchema

# 1. Fetch customer info by customer_id
async def sp_get_customer_info(conn, customer_id):
    try:
        sql = text("CALL CBS_GetCustomerInfo(:p_customer_id)")
        result = await conn.execute(sql, {"p_customer_id": customer_id})
        if result is not None:
            row = result.fetchone()
        return CBSCustomerInfoSchema(**dict(row._mapping)) if row else None
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_info",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 2. Fetch customer addresses by customer_id
async def sp_get_customer_addresses(conn, customer_id):
    try:
        sql = text("CALL CBS_GetCustomerAddresses(:p_customer_id)")
        result = await conn.execute(sql, {"p_customer_id": customer_id})
        rows = result.fetchall()
        return [CBSCustomerAddressSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_addresses",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 3. Fetch customer emails by customer_id
async def sp_get_customer_emails(conn, customer_id):
    try:
        sql = text("CALL CBS_GetCustomerEmails(:p_customer_id)")
        result = await conn.execute(sql, {"p_customer_id": customer_id})
        rows = result.fetchall()
        return [CBSCustomerEmailSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_emails",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 4. Fetch customer phones by customer_id
async def sp_get_customer_phones(conn, customer_id):
    try:
        sql = text("CALL CBS_GetCustomerPhones(:p_customer_id)")
        result = await conn.execute(sql, {"p_customer_id": customer_id})
        rows = result.fetchall()
        return [CBSCustomerPhoneSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_phones",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 5. Fetch customer accounts with details by customer_id and product_category
async def sp_get_customer_accounts_with_details(conn, customer_id, product_category=None):
    try:
        sql = text("CALL CBS_GetCustomerAccountsWithDetails(:p_customer_id, :p_product_category)")
        pc = product_category if product_category else ""
        result = await conn.execute(sql, {"p_customer_id": customer_id, "p_product_category": pc})
        rows = result.fetchall()
        return [CBSAccountFullDetailsSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_accounts_with_details",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 6. Fetch customer accounts by customer_id and product_category
async def sp_get_customer_accounts(conn, customer_id, product_category=None):
    try:
        sql = text("CALL CBS_GetCustomerAccounts(:p_customer_id, :p_product_category)")
        pc = product_category if product_category else ""
        result = await conn.execute(sql, {"p_customer_id": customer_id, "p_product_category": pc})
        rows = result.fetchall()
        return [CBSCustomerAccountsSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_customer_accounts",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 7. Fetch account info by account_number
async def sp_get_account_info(conn, account_number):
    try:
        sql = text("CALL CBS_GetAccountInfo(:p_account_number)")
        result = await conn.execute(sql, {"p_account_number": account_number})
        if result is not None:
            row = result.fetchone()
        return CBSAccountDetailsSchema(**dict(row._mapping)) if row else None
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_account_info",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 8. Fetch balances and interest rate by account_number
async def sp_get_account_balances_and_rate(conn, account_number):
    try:
        sql = text("CALL CBS_GetAccountBalancesAndRate(:p_account_number)")
        result = await conn.execute(sql, {"p_account_number": account_number})
        if result is not None:
            row = result.fetchone()
        return CBSAccountBalanceDetailsSchema(**dict(row._mapping)) if row else None
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_account_balances_and_rate",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 9. Fetch only available balance by account_number
async def sp_get_available_balance(conn, account_number):
    try:
        sql = text("CALL CBS_GetAvailableBalance(:p_account_number)")
        result = await conn.execute(sql, {"p_account_number": account_number})
        if result is not None:
            row = result.fetchone()
        if row:
            row_dict = dict(row._mapping)
            return float(row_dict.get("available_balance", "0"))
        else:
            return 0.0
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_available_balance",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 10. Fetch Account Wise Trans Limit info by account_number
async def sp_get_account_wise_trans_limit_info(conn, account_number):
    try:
        sql = text("CALL CBS_GetAccountWiseTransLimitInfo(:p_account_number)")
        result = await conn.execute(sql, {"p_account_number": account_number})
        if result is not None:
            row = result.fetchone()
        return CBSAccountWiseTransLimitInfoSchema(**dict(row._mapping)) if row else None
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CallSPServices/sp_get_account_wise_trans_limit_info",
            CreatedBy = ""
        ))
        raise Exception(ex)

# 11. Fund Transfer
async def sp_fund_transfer(conn, data: FundTransferViewModelSchema):
    try:
        await conn.execute(text("SET @o_TRANS_ID = NULL, @o_ERROR_MSG = NULL;"))

        sql_call = text("""
            CALL CBS_FundTransfer(
                :p_FROM_ACCOUNT,
                :p_SENDER_NAME,
                :p_TO_ACCOUNT,
                :p_RECEIVER_NAME,
                :p_TRANS_MODE,
                :p_PURPOSE,
                :p_AMOUNT,
                :p_CURRENCY_NM,
                @o_TRANS_ID,
                @o_ERROR_MSG
            )
        """)
        params = {
            "p_FROM_ACCOUNT": data.FromAccount,
            "p_SENDER_NAME": data.SenderName,
            "p_TO_ACCOUNT": data.ToAccount,
            "p_RECEIVER_NAME": data.ReceiverName,
            "p_TRANS_MODE": "TRANSFER",
            "p_PURPOSE": data.Pourpose,
            "p_AMOUNT": data.Amount,
            "p_CURRENCY_NM": data.Currency
        }
        await conn.execute(sql_call, params)

        result = await conn.execute(text("SELECT @o_TRANS_ID AS TRANS_ID, @o_ERROR_MSG AS ERROR_MSG"))
        if result is not None:
            output = result.fetchone()

        if output.ERROR_MSG:
            raise Exception(output.ERROR_MSG)

        return output.TRANS_ID

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_fund_transfer",
            CreatedBy=""
        ))
        raise Exception(ex)


# 12. Fetch Account Wise Transaction History between dates
async def sp_get_account_transaction_history(conn, account_number, start_date, end_date, sort_direction):
    try:
        sql = text("""
            CALL CBS_GetAccountTransactionHistory(
                :p_account_number,
                :p_start_date,
                :p_end_date,
                :p_sort_direction
            )
        """)
        params = {
            "p_account_number": account_number,
            "p_start_date": start_date,
            "p_end_date": end_date,
            "p_sort_direction": sort_direction
        }
        result = await conn.execute(sql, params)
        rows = result.fetchall()
        return [CBSTransactionHistorySchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_account_transaction_history",
            CreatedBy=""
        ))
        raise Exception(ex)

# 13. Fetch branch list
async def sp_get_branch_list_with_details(conn):
    try:
        sql = text("CALL CBS_GetBranchListWithDetails()")
        result = await conn.execute(sql)
        rows = result.fetchall()
        return [CBSBranchDetailsSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_branch_list_with_details",
            CreatedBy=""
        ))
        raise Exception(ex)

