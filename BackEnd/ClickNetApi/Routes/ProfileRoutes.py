import io
import os
from base64 import b64decode, b64encode
from datetime import datetime
import traceback
from typing import Optional
from PIL import Image
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import and_, delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from Config.dbConnection import AsyncSessionLocalClickNet
from Models.shared import customerPhotos, systemActivity
from Schemas.Enums.Enums import ActivityType
from Schemas.shared import StatusResult, SystemActivitySchema, SystemLogErrorSchema, CustomerPhotoSchema, CustomerActivityViewModelSchema
from Services.ActivityServices import AddActivityLog
from Services.GenericCRUDServices import GenericInserter, GenericUpdater
from Services.JWTTokenServices import ValidateJWTToken
from Services.LogServices import AddLogOrError
from Services.CommonServices import GetCurrentActiveSession, GetErrorMessage, EncryptImage, DecryptImage
from Services.CBSServices import GetCustomerFullInformation
from Cache.AppSettingsCache import Get

customerPhotosUpdater = GenericUpdater[CustomerPhotoSchema, type(customerPhotos)]()

ProfileRoutes = APIRouter(prefix="/Profile")

@ProfileRoutes.get("/FetchCustomerInfo")
async def FetchCustomerInfo(currentCustuserprofile=Depends(ValidateJWTToken)) -> StatusResult:
    status = StatusResult()
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        customerInfo = await GetCustomerFullInformation(currentCustuserprofile.customer_id)
        if customerInfo: 
            status.Status = "OK"
            status.Message = "Fetched customer information."
            status.Result = customerInfo
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.PROFILE,
                Title="Successfully fetched customer information",
                Details=f"{currentCustuserprofile.user_id.lower()} successfully fetched customer information",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CustomerProfile/FetchCustomerInfo",
            CreatedBy=currentCustuserprofile.user_id.lower()
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.PROFILE,
            Title="Failed to fetch customer information",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch customer information",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    return status

@ProfileRoutes.get("/FetchCustomerActivityList/")
async def FetchCustomerActivityList(count:int, activity_type: Optional[ActivityType] = None, currentCustuserprofile=Depends(ValidateJWTToken)) -> StatusResult:
    status = StatusResult()
    db_session = None
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)

        if not session:
            raise ValueError("Invalid Token or Session Expired.")
        
        activities = []
        db_session = AsyncSessionLocalClickNet()
        conditions = [systemActivity.c.USER_ID == currentCustuserprofile.user_id]

        if activity_type:
            conditions.append(systemActivity.c.ACTIVITY_TYPE == activity_type)

        stmt = (
            select(
                systemActivity.c.ACTIVITY_TYPE,
                systemActivity.c.ACTIVITY_TITLE,
                systemActivity.c.ACTIVITY_DT,
                systemActivity.c.REQUESTED_FROM
            )
            .where(and_(*conditions))
            .order_by(desc(systemActivity.c.ACTIVITY_DT))
            .limit(count)
        )
        result = await db_session.execute(stmt)
        rows = result.fetchall()
        if rows:
            activities = [CustomerActivityViewModelSchema(**dict(row._mapping)) for row in rows]
        
        if activities: 
            status.Status = "OK"
            status.Message = "Fetched customer activities."
            status.Result = activities
            
            await AddActivityLog(SystemActivitySchema(
                Type=ActivityType.PROFILE,
                Title="Successfully fetched customer activities",
                Details=f"{currentCustuserprofile.user_id.lower()} successfully fetched customer activities",
                IpAddress=session.ip_address if session else "",
                UserType="USER",
                User_Id=currentCustuserprofile.user_id.lower()
            ))
        else:
            raise ValueError("No data found.")

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CustomerProfile/FetchCustomerActivityList",
            CreatedBy=currentCustuserprofile.user_id.lower()
        ))
        
        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.PROFILE,
            Title="Failed to fetch customer activities",
            Details=f"{currentCustuserprofile.user_id.lower()} is failed to fetch customer activities",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    finally:
        if db_session:
            await db_session.close()
    return status

@ProfileRoutes.post("/SaveCustomerProfilePicture")
async def SaveCustomerProfilePicture(photo: UploadFile = File(...), currentCustuserprofile=Depends(ValidateJWTToken)) -> StatusResult:
    status = StatusResult()
    db_session = None
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)
        if not session:
            raise ValueError("Invalid Token or Session Expired.")

        # Read file bytes
        image = Image.open(photo.file)

        # Resize the image to 180x180 
        max_size = (180, 180)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save compressed image to bytes buffer
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG', quality=100, optimize=True)
        compressed_image_bytes = img_byte_arr.getvalue()

        # Encrypt image bytes
        encrypted_image = await EncryptImage(compressed_image_bytes)

        # Define a directory to save encrypted images
        save_dir = os.path.join(Get("CUSTOMER_PHOTO_PATH"), currentCustuserprofile.user_id.lower())
        os.makedirs(save_dir, exist_ok=True)

        # Generate a unique filename (e.g. user_id + timestamp)
        filename = f"{currentCustuserprofile.user_id.lower()}_{int(datetime.now().timestamp())}.bin"
        filepath = os.path.join(save_dir, filename)

        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(
            select(customerPhotos)
            .where(func.lower(customerPhotos.c.USER_ID) == currentCustuserprofile.user_id.lower())
        )
        if result is not None:
            row = result.fetchone()
        
        customerNewPhoto = CustomerPhotoSchema(**dict(row._mapping)) if row else None

        # Save only file path to DB
        if not customerNewPhoto:
            customerNewPhoto = CustomerPhotoSchema(
                user_id=currentCustuserprofile.user_id.lower(),
                photo_path=filepath,
                create_by=currentCustuserprofile.user_id.lower(),
                create_at=datetime.now()
            )

            await GenericInserter[CustomerPhotoSchema].insert_record(
                table=customerPhotos,
                schema_model=CustomerPhotoSchema,
                data=customerNewPhoto,
                returning_fields=[]
            )
        else:
            customerNewPhoto.photo_path = filepath 
            customerNewPhoto.create_by = currentCustuserprofile.user_id.lower()
            customerNewPhoto.create_at = datetime.now()
            await customerPhotosUpdater.update_record(
                table=customerPhotos,
                schema_model=CustomerPhotoSchema,
                record_id=customerNewPhoto.user_id,
                update_data=customerNewPhoto,
                id_column="USER_ID",
                exclude_fields={}
            )
        
        await db_session.commit()

        # Write encrypted image bytes to file
        with open(filepath, "wb") as f:
            f.write(encrypted_image)

        status.Status = "OK"
        status.Message = "Profile picture saved."
        status.Result = None

        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.PROFILE,
            Title="Successfully saved profile picture",
            Details=f"{currentCustuserprofile.user_id.lower()} successfully saved profile picture",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)

        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CustomerProfile/SaveCustomerProfilePicture",
            CreatedBy=currentCustuserprofile.user_id.lower()
        ))

        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.PROFILE,
            Title="Failed to save profile picture",
            Details=f"{currentCustuserprofile.user_id.lower()} failed to save profile picture",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    finally:
        if db_session:
            await db_session.close()

    return status

@ProfileRoutes.get("/FetchCustomerProfilePicture")
async def FetchCustomerProfilePicture(currentCustuserprofile=Depends(ValidateJWTToken)) -> StatusResult:
    status = StatusResult()
    db_session = None
    try:
        session = await GetCurrentActiveSession(currentCustuserprofile.user_id)
        if not session:
            raise ValueError("Invalid Token or Session Expired.")

        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(
            select(customerPhotos.c.PHOTO_PATH)
            .where(func.lower(customerPhotos.c.USER_ID) == currentCustuserprofile.user_id.lower())
        )
        if result is not None:
            row = result.fetchone()

        if not row or not row.PHOTO_PATH:
            raise ValueError("Profile picture not found.")

        filepath = row.PHOTO_PATH
        if not os.path.exists(filepath):
            raise ValueError("Profile picture file not found on server.")

        # Read encrypted bytes from file
        with open(filepath, "rb") as f:
            encrypted_image = f.read()

        # Decrypt image bytes
        decrypted_image = await DecryptImage(encrypted_image)

        # Encode to base64 for sending over API
        base64_image = b64encode(decrypted_image).decode('utf-8')

        status.Status = "OK"
        status.Message = "Profile picture fetched."
        status.Result = base64_image

        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.PROFILE,
            Title="Successfully fetched profile picture",
            Details=f"{currentCustuserprofile.user_id.lower()} successfully fetched profile picture",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)

        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CustomerProfile/FetchCustomerProfilePicture",
            CreatedBy=currentCustuserprofile.user_id.lower()
        ))

        await AddActivityLog(SystemActivitySchema(
            Type=ActivityType.PROFILE,
            Title="Failed to fetch profile picture",
            Details=f"{currentCustuserprofile.user_id.lower()} failed to fetch profile picture",
            IpAddress=session.ip_address if session else "",
            UserType="USER",
            User_Id=currentCustuserprofile.user_id.lower()
        ))
    finally:
        if db_session:
            await db_session.close()

    return status