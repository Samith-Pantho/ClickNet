import traceback
from Config.dbConnection import AsyncSessionLocalClickKyc
from sqlalchemy.ext.asyncio import AsyncSession
from .LogServices import AddLogOrError
from Schemas.shared import SystemLogErrorSchema, AppSettingViewModelSchema
from .CallClickKycSPServices import sp_get_app_settings_by_keys

async def FetchAppSettingsByKeys(keys: str) -> AppSettingViewModelSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalClickKyc()
        return await sp_get_app_settings_by_keys(db_session, keys)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "AppSettingsServices/FetchAppSettingsByKeys",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()