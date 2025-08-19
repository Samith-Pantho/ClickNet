from pydantic import BaseModel, Field
from typing import Optional

class SystemCaptchaLogSchema(BaseModel):
    sl: Optional[int] = Field(None, alias="SL")
    uuid: Optional[str] = Field(None, alias="UUID")
    status: Optional[bool] = Field(False, alias="STATUS")

    class Config:
        populate_by_name = True
