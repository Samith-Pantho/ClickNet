import json
import os
import traceback
import httpx
from sqlalchemy import select
from Models.shared import systemCaptchaLog
from Schemas.shared import SystemLogErrorSchema, SystemCaptchaLogSchema
from .CommonServices import ApiCall, GetSha1Hash, GetTableSl
from .GenericCRUDServices import GenericInserter, GenericUpdater
from .LogServices import AddLogOrError
from dotenv import load_dotenv # type: ignore
from Cache.AppSettingsCache import Get
from sqlalchemy.ext.asyncio import AsyncSession
from Config.dbConnection import AsyncSessionLocalClickNet

systemCaptchaLogUpdater = GenericUpdater[SystemCaptchaLogSchema, type(systemCaptchaLog)]()

load_dotenv()

APIWEBHOOK_URL = os.getenv("APIWEBHOOK_URL", "http://apiwebhook:9999")

async def VerifyCaptchaToken(token: str) -> bool:
    db_session = None
    captcha = SystemCaptchaLogSchema()
    try:
        hashToken = await GetSha1Hash(token)
        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(
                select(systemCaptchaLog)
                .where(systemCaptchaLog.c.UUID == hashToken)
            )
        if result is not None:
            row = result.fetchone()
        
        if row:
            captcha = SystemCaptchaLogSchema(**dict(row._mapping))
        
        if captcha and captcha.status:
            return True
        else:
            payload = {
                "token": token
            }
            headers = {
                "accept": "application/json",
                "x-api-key":  Get("API_WEBHOOK_KEY"),
                "content-type": "application/json"
            }
            
            status = await ApiCall(
                method="POST",
                url=f"{APIWEBHOOK_URL}/Webhook/VerifyCaptcha",
                headers=headers,
                payload=payload
            )
            isHuman = status.get("Result")
                    
            if not isHuman:
                await AddLogOrError(SystemLogErrorSchema(
                    Msg=json.dumps(result),
                    Type = "LOG",
                    ModuleName = "CaptchaService/VerifyCaptchaToken",
                    CreatedBy = ""
                ))
                
            if captcha is None:
                captcha = SystemCaptchaLogSchema()
            
            captcha.sl= await GetTableSl("systemCaptchaLog")
            captcha.uuid=hashToken
            captcha.status=isHuman
            await GenericInserter[SystemCaptchaLogSchema].insert_record(
                table=systemCaptchaLog,
                schema_model=SystemCaptchaLogSchema,
                data=captcha,
                returning_fields=[]
            )

            return isHuman
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CaptchaService/VerifyCaptchaToken",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()


async def DisableCaptchaToken(token: str):
    db_session = None
    captcha = SystemCaptchaLogSchema()
    try:
        hashToken = await GetSha1Hash(token)
        db_session = AsyncSessionLocalClickNet()
        result = await db_session.execute(
                select(systemCaptchaLog)
                .where(systemCaptchaLog.c.UUID == hashToken)
            )
        if result is not None:
            row = result.fetchone()
        
        if row:
            captcha = SystemCaptchaLogSchema(**dict(row._mapping))
        
        if captcha and captcha.status:
            captcha.status = False
            await systemCaptchaLogUpdater.update_record(
                table=systemCaptchaLog,
                schema_model=SystemCaptchaLogSchema,
                record_id=captcha.sl,
                update_data=captcha,
                id_column="SL",
                exclude_fields={}
            )

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CaptchaService/VerifyCaptchaToken",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()
