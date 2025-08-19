import os
from datetime import datetime
import traceback
from Config.dbConnection import AsyncSessionLocalClickNet
from sqlalchemy.ext.asyncio import AsyncSession
from Models.shared import systemActivity
from Schemas.shared import SystemLogErrorSchema, SystemActivitySchema
from Services.CommonServices import GetTableSl
from .LogServices import AddLogOrError

async def AddActivityLog(data: SystemActivitySchema):
    db_session = None
    try:
        db_session = AsyncSessionLocalClickNet()
        insert_new_activity = systemActivity.insert().values(
                ACTIVITY_TYPE=data.Type,
                ACTIVITY_TITLE=data.Title,
                ACTIVITY_DETAILS=data.Details,
                ACTIVITY_DT=datetime.now(),
                REQUESTED_FROM=data.IpAddress,
                USER_TYPE=data.UserType,
                USER_ID=(data.User_Id or "").lower()
            )

        await db_session.execute(insert_new_activity)
        await db_session.commit()

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "ActivityServices/AddActivityLog",
            CreatedBy = (data.User_Id or "").lower()
        ))
    finally:
        if db_session:
            await db_session.close()