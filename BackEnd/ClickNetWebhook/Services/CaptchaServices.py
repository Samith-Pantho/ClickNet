import traceback
from typing import Any, Dict
import httpx
from Schemas.shared import SystemLogErrorSchema
from .LogServices import AddLogOrError
from dotenv import load_dotenv # type: ignore
from Cache.AppSettingsCache import Get

async def VerifyCaptchaToken(data: Dict[str, Any]) -> bool:
    try:
        url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            "secret": Get("GOOGLE_RECAPTCHA_SECRET_KEY"),
            "response": data.get("token")
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            result = response.json()
            
        return result.get("success", False)
            
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CaptchaService/VerifyCaptchaToken",
            CreatedBy = ""
        ))
        return None