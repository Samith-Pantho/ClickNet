from datetime import datetime
import traceback
from Config.dbConnection import AsyncSessionLocalClickKyc
from sqlalchemy.ext.asyncio import AsyncSession
from .LogServices import AddLogOrError

from Schemas.shared import SystemLogErrorSchema, CustomerRegistrationSchema

from .CallClickKycSPServices import sp_get_tracking_data, sp_update_tracking_data

async def GetTrackingData(tracking_id: str) -> CustomerRegistrationSchema:
    db_session = None
    try:
        db_session = AsyncSessionLocalClickKyc()
        return await sp_get_tracking_data(db_session, tracking_id)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "KYCServices/GetTrackingData",
            CreatedBy = tracking_id
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def UpdateTrackingData(data:CustomerRegistrationSchema) -> str:
    db_session = None
    try:
        db_session = AsyncSessionLocalClickKyc()
        return await sp_update_tracking_data(db_session, data)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "KYCServices/UpdateTrackingData",
            CreatedBy = data.tracking_id
        ))
        return None
    finally:
        if db_session:
            await db_session.close()