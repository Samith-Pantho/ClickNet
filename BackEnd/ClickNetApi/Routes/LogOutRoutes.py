import traceback
from fastapi import APIRouter, Depends
from Schemas.Enums.Enums import ActivityType
from Models.shared import customerSession
from Schemas.shared import StatusResult, SystemLogErrorSchema, SystemActivitySchema, CustomoerSessionSchema
from Services.ActivityServices import AddActivityLog
from Services.CommonServices import GetCurrentActiveSession, GetErrorMessage
from Services.GenericCRUDServices import GenericUpdater
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError

customerSessionUpdater = GenericUpdater[CustomoerSessionSchema, type(customerSession)]()

LogOutRoutes = APIRouter(prefix="/Logout")

@LogOutRoutes.get("/Logout")
async def Logout(currentCustuserprofile=Depends(ValidateJWTToken)):
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")

        session.active_flag = 0
        session.status = 0
        session.remarks = f"Logged out from {session.ip_address}."
        await customerSessionUpdater.update_record(
            table=customerSession,
            schema_model=CustomoerSessionSchema,
            record_id=session.session_id,
            update_data=session,
            id_column="SESSION_ID",
            exclude_fields={}
        )
        
        status.Status = "OK"
        status.Message = "Successfully logged out"
        status.Result = None
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.LOGOUT,
            Title="Successfully logged out",
            Details=f"{currentCustuserprofile.user_id.lower()} is successfully logged out.",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="LogoutRoutes/Logout",
            CreatedBy=currentCustuserprofile.user_id.lower()
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.LOGOUT,
            Title="Failed to logout",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to logout. Reason : " + await GetErrorMessage(ex),
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status