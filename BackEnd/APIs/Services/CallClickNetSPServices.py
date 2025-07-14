from datetime import datetime
from decimal import Decimal
from sqlalchemy.sql import text
from Schemas.shared import CustomerOtpSchema, SystemLogErrorSchema
from .LogServices import AddLogOrError

def sp_get_pending_otp(conn, data:CustomerOtpSchema, cutofftime:datetime):
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

        result = conn.execute(sql, params)
        row = result.fetchone()

        return CustomerOtpSchema(**dict(row._mapping)) if row else None

    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg=str(ex),
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_pending_otp",
            CreatedBy=""
        ))
        raise Exception(ex)
