import traceback
from Config.dbConnection import AsyncSessionLocalCBS
from sqlalchemy.ext.asyncio import AsyncSession
from Schemas.shared import SystemLogErrorSchema, CustomerAddMoneySchema
from .CallSPServices import sp_gl_to_account_transfer
from .LogServices import AddLogOrError


async def CBSAddMoneyFromGl(data:CustomerAddMoneySchema) -> str:
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_gl_to_account_transfer(db_session, data)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/CBSAddMoneyFromGl",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()