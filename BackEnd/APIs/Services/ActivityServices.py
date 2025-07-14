import os
from datetime import datetime
from Config.dbConnection import engine 
from Models.shared import systemActivity
from Schemas.shared import SystemLogErrorSchema, SystemActivitySchema
from .LogServices import AddLogOrError

def AddActivityLog(data: SystemActivitySchema):
    try:
        insert_new_activity = systemActivity.insert().values(
                ACTIVITY_TYPE=data.Type,
                ACTIVITY_TITLE=data.Title,
                ACTIVITY_DETAILS=data.Details,
                ACTIVITY_DT=datetime.now(),
                REQUESTED_FROM=data.IpAddress,
                USER_TYPE=data.UserType,
                USER_ID=(data.User_Id or "").lower()
            )

        with engine.begin() as _conn:
            _conn.execute(insert_new_activity)

    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "ActivityServices/AddActivityLog",
            CreatedBy = (data.User_Id or "").lower()
        ))