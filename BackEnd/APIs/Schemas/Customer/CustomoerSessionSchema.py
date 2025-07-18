from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class CustomoerSessionSchema(BaseModel):
    user_id: Optional[str] = Field(None, alias="USER_ID")
    session_id: Optional[str] = Field(None, alias="SESSION_ID")
    start_time: Optional[datetime] = Field(None, alias="START_TIME")
    last_access_time: Optional[datetime] = Field(None, alias="LAST_ACCESS_TIME")
    ip_address: Optional[str] = Field(None, alias="IP_ADDRESS")
    active_flag: Optional[Decimal] = Field(None, alias="ACTIVE_FLAG")
    remarks: Optional[str] = Field(None, alias="REMARKS")
    status: Optional[int] = Field(None, alias="STATUS")
    create_by: Optional[str] = Field(None, alias="CREATE_BY")
    create_dt: Optional[datetime] = Field(None, alias="CREATE_DT")

    class Config:
        populate_by_name = True 
