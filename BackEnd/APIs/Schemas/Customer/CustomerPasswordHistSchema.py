from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerPasswordHistSchema(BaseModel):
    user_id: Optional[str] = Field(None, alias="USER_ID")
    passward_string: Optional[str] = Field(None, alias="PASSWARD_STRING")
    status: Optional[int] = Field(None, alias="STATUS")
    create_by: Optional[str] = Field(None, alias="CREATE_BY")
    create_dt: Optional[datetime] = Field(None, alias="CREATE_DT")

    class Config:
        populate_by_name = True
