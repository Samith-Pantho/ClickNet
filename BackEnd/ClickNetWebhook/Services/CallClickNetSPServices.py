import traceback
from sqlalchemy.sql import text
from Schemas.shared import SystemLogErrorSchema
from .LogServices import AddLogOrError

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
    