
import traceback
from sqlalchemy import text
from .LogServices import AddLogOrError
from Schemas.shared import SystemLogErrorSchema, CustomerAddMoneySchema


async def sp_gl_to_account_transfer(conn, data: CustomerAddMoneySchema):
    try:
        # Initialize output variables
        await conn.execute(text("SET @o_TRANS_ID = NULL, @o_ERROR_MSG = NULL;"))

        # Call the stored procedure
        sql_call = text("""
            CALL CBS_GLToAccountTransfer(
                :p_TO_ACCOUNT,
                :p_RECEIVER_NAME,
                :p_AMOUNT_CENTS,
                :p_CURRENCY,
                :p_VENDOR,
                @o_TRANS_ID,
                @o_ERROR_MSG
            )
        """)
        
        params = {
            "p_TO_ACCOUNT": data.receiver_no,
            "p_RECEIVER_NAME": data.receiver_name,
            "p_AMOUNT_CENTS": data.amount_in_cent,
            "p_CURRENCY": data.currency,
            "p_VENDOR": data.payment_via
        }
        
        await conn.execute(sql_call, params)

        # Get the output parameters
        result = await conn.execute(
            text("SELECT @o_TRANS_ID AS TRANS_ID, @o_ERROR_MSG AS ERROR_MSG")
        )
        output = result.fetchone()

        if output.ERROR_MSG:
            raise Exception(output.ERROR_MSG)

        return output.TRANS_ID

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_gl_to_account_transfer",
            CreatedBy=""
        ))
        raise Exception(ex)