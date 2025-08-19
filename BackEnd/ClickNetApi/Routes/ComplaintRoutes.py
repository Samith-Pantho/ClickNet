import traceback
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, insert
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from Config.dbConnection import AsyncSessionLocalClickNet 
from Models.shared import customerComplaints
from Schemas.Enums.Enums import ActivityType
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema, CustomerComplaintsSchema, ComplaintViewModelSchema
from Services.ActivityServices import AddActivityLog
from Services.GenericCRUDServices import GenericInserter
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError
from Services.CommonServices import GetCurrentActiveSession, GetErrorMessage, GetTableSl

ComplaintRoutes = APIRouter(prefix="/Request")

@ComplaintRoutes.post("/CreateComplaint")
async def CreateComplaint(data: ComplaintViewModelSchema, currentCustuserprofile=Depends(ValidateJWTToken)) -> StatusResult:
    status = StatusResult()
    try:
        # Get user session
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)
        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        # Create complaint object
        newComplaint = CustomerComplaintsSchema(
            id= await GetTableSl("customerComplaints"),
            user_id=currentCustuserprofile.user_id,
            category=data.category,
            description=data.description,
            status="OPEN",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Insert complaint 
        await GenericInserter[CustomerComplaintsSchema].insert_record(
            table=customerComplaints,
            schema_model=CustomerComplaintsSchema,
            data=newComplaint,
            returning_fields=[]
        )

        status.Status = "OK"
        status.Message = "Complaint submitted successfully."
        
        # Log activity
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.REQUEST,
            Title="Successfully added a complaint",
            Details=f"{currentCustuserprofile.user_id.lower()} successfully added a complaint for {data.category}",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        
        # Log error
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="ComplaintRoutes/CreateComplaint",
            CreatedBy=currentCustuserprofile.user_id.lower()
        ))
        
        # Log failed activity
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.REQUEST,
            Title="Failed to add a complaint",
            Details=f"{currentCustuserprofile.user_id.lower()} failed to add a complaint. Reason: {await GetErrorMessage(ex)}",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    
    return status


@ComplaintRoutes.get("/Complaints")
async def Complaints(currentCustuserprofile=Depends(ValidateJWTToken)) -> StatusResult:
    status = StatusResult()
    db_session = None
    try:
        # Get user session
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)
        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        # Fetch complaints using async session
        db_session = AsyncSessionLocalClickNet()

        query = select(customerComplaints).where(
            func.lower(customerComplaints.c.USER_ID) == currentCustuserprofile.user_id.lower()
        )

        result = await db_session.execute(query)
        complaints_data = result.fetchall()

        complaints = [CustomerComplaintsSchema(**dict(row._mapping)) for row in complaints_data] if complaints_data else []

        status.Status = "OK"
        status.Message = None
        status.Result = complaints
        
        # Log activity
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.REQUEST,
            Title="Successfully fetched all complaints",
            Details=f"{currentCustuserprofile.user_id.lower()} successfully fetched all complaints",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
        
        # Log error
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="ComplaintRoutes/Complaints",
            CreatedBy=currentCustuserprofile.user_id.lower()
        ))
        
        # Log failed activity
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.REQUEST,
            Title="Failed to fetch all complaints",
            Details=f"{currentCustuserprofile.user_id.lower()} failed to fetch complaints. Reason: {await GetErrorMessage(ex)}",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    finally:
        if db_session:
            await db_session.close()
    
    return status