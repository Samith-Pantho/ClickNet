import traceback
from typing import List
from fastapi import APIRouter, HTTPException, Query
from Schemas.shared import StatusResult, SystemLogErrorSchema
from Services.CBSServices import GetBranchList
from Services.CommonServices import GetDecryptedText, GetErrorMessage
from Services.LogServices import AddLogOrError
from Services.AppSettingsServices import FetchAppSettingsByKeys

AppConfigRoutes = APIRouter(prefix="/AppConfig")

@AppConfigRoutes.get("/GetAppSettingsByKeys")
async def GetAppSettingsByKeys(keys: List[str] = Query(...)):
    result = StatusResult()
    try:
        key_string = ",".join(keys)
        value = await FetchAppSettingsByKeys(key_string)

        if value is not None:
            result.Status = "OK"
            result.Message = "Found in APP_SETTINGS"
            result.Result = value
        else:
            result.Status = "FAILED"
            result.Message = "Not found in APP_SETTINGS"
            result.Result = None
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "AppConfig/GetAppSettingsByKey",
            CreatedBy = ""
        ))
        result.Status = "FAILED"
        result.Message = "Something went wrong."
        result.Result = None

    return result
    

@AppConfigRoutes.get("/GetBranches")
async def GetBranches():
    status = StatusResult()
    try:
        branches = await GetBranchList()

        if branches is not None:
            status.Status = "OK"
            status.Message = ""
            status.Result = branches
        else:
            raise ValueError("No data found.")
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "AppConfigRoutes/GetBranchList",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None

    return status
