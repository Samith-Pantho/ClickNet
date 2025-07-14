from fastapi import APIRouter, HTTPException
from Schemas.shared import StatusResult, SystemLogErrorSchema
from Services.LogServices import AddLogOrError
from Services.AppSettingsServices import FetchAppSettingsByKey
from Services.CommonServices import LoadJsonFromFile

AppConfigRoutes = APIRouter(prefix="/AppConfig")

@AppConfigRoutes.get("/GetAppSettingsByKey/{key}")
async def GetAppSettingsByKey(key:str):
    try:
        result = StatusResult[str]()
        value = FetchAppSettingsByKey(key)

        if value is not None:
            result.Status = "OK"
            result.Message = f"{key} value found in APP_SETTINGS"
            result.Result = value
        else:
            result.Status = "FAILED"
            result.Message = f"{key} value not found in APP_SETTINGS"
            result.Result = None
            
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "AppConfig/GetAppSettingsByKey",
            CreatedBy = ""
        ))
        result.Status = "FAILED"
        result.Message = "Something went wrong."
        result.Result = None

    return result
    

@AppConfigRoutes.get("/GetAppConfigs")
async def GetAppConfigs():
    try:
        result = StatusResult[object]()
        appConfigs = LoadJsonFromFile("appConfigs")
        
        if appConfigs:
            result.Status = "OK"
            result.Message = ""
            result.Result = appConfigs
        else:
            result.Status = "FAILED"
            result.Message = "Not Found"
            result.Result = None

    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "AppConfig/GetAppConfigs",
            CreatedBy = ""
        ))
        result.Status = "FAILED"
        result.Message = "Something went wrong."
        result.Result = None

    return result
    
@AppConfigRoutes.get("/GetMainMenu")
async def GetMainMenu():
    try:
        result = StatusResult[object]()
        mainMenu = LoadJsonFromFile("mainMenu")

        if mainMenu:
            result.Status = "OK"
            result.Message = ""
            result.Result = mainMenu
        else:
            result.Status = "FAILED"
            result.Message = "Not Found"
            result.Result = None

    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "AppConfig/GetMainMenu",
            CreatedBy = ""
        ))
        result.Status = "FAILED"
        result.Message = "Something went wrong."
        result.Result = None

    return result
    
@AppConfigRoutes.get("/GetCustomerRequestMenu")
async def GetCustomerRequestMenu():
    try:
        result = StatusResult[object]()
        customerRequestMenu = LoadJsonFromFile("customerRequestMenu")

        if customerRequestMenu:
            result.Status = "OK"
            result.Message = ""
            result.Result = customerRequestMenu
        else:
            result.Status = "FAILED"
            result.Message = "Not Found"
            result.Result = None

    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "AppConfig/GetCustomerRequestMenu",
            CreatedBy = ""
        ))
        result.Status = "FAILED"
        result.Message = "Something went wrong."
        result.Result = None

    return result
    
@AppConfigRoutes.get("/GetApplicationMenu")
async def GetApplicationMenu():
    try:
        result = StatusResult[object]()
        
        raise HTTPException(status_code=501, detail="Not Yet Implemented.")

    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "AppConfig/GetApplicationMenu",
            CreatedBy = ""
        ))
        result.Status = "FAILED"
        result.Message = "Something went wrong."
        result.Result = None

    return result