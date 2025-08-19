from datetime import datetime
from decimal import Decimal
import traceback
from sqlalchemy.sql import text
from Schemas.shared import CustomerOtpSchema, SystemLogErrorSchema, AppSettingViewModelSchema
from .LogServices import AddLogOrError

async def sp_get_pending_otp(conn, data:CustomerOtpSchema, cutofftime:datetime):
    try:
        sql = text("""
            CALL CLICKNET_GetPendingOTP(
                :p_user_id,
                :p_cust_id,
                :p_from_acct,
                :p_from_branch,
                :p_to_acct,
                :p_to_branch,
                :p_to_bank_id,
                :p_to_routing_numb,
                :p_amount_ccy,
                :p_amount_lcy,
                :p_cutoff_time
            )
        """)
        
        params = {
            "p_user_id": data.user_id.strip().lower(),
            "p_cust_id": data.cust_id,
            "p_from_acct": data.from_account_no,
            "p_from_branch": data.from_branch_id,
            "p_to_acct": data.to_account_no,
            "p_to_branch": data.to_branch_id,
            "p_to_bank_id": data.to_bank_id,
            "p_to_routing_numb": data.to_routing_numb,
            "p_amount_ccy": round(Decimal(data.amount_ccy or "0.0"), 4),
            "p_amount_lcy": round(Decimal(data.amount_lcy or "0.0"), 4),
            "p_cutoff_time": cutofftime
        }

        result = await conn.execute(sql, params)
        if result is not None:
            row = result.fetchone()
        if row:
            return CustomerOtpSchema(**dict(row._mapping))  
        else: 
            raise ValueError("No Data Found")

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_pending_otp",
            CreatedBy=""
        ))
        raise Exception(ex)

async def sp_get_app_settings_by_keys(conn, keys: str):
    try:
        sql = text("CALL CLICKNET_GetAppSettingsByKeys(:p_keys)")
        result = await conn.execute(sql, {"p_keys": keys})
        rows = result.fetchall()
        return [AppSettingViewModelSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_app_settings_by_keys",
            CreatedBy=""
        ))
        raise Exception(ex)

async def sp_get_all_app_settings(conn):
    try:
        sql = text("CALL CLICKNET_GetAllAppSettings()")
        result = await conn.execute(sql)
        rows = result.fetchall()
        return [{"KEY": row[0], "VALUE": row[1]} for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_all_app_settings",
            CreatedBy=""
        ))
        raise Exception(ex)
    
async def sp_get_table_sl(conn, table_nm: str) -> int | None:
    try:
        result = await conn.execute(text("CALL CLICKNET_GetTableSl(:table_nm)"), {"table_nm": table_nm})
        row = result.fetchone()
        sl = row.output_sl if row else None
        print(f"{table_nm}-{sl}")
        return sl
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_table_sl",
            CreatedBy=""
        ))
        return None