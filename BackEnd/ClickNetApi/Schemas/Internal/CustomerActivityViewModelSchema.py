from pydantic import BaseModel, Field
from typing import Optional
from datetime import  datetime

class CustomerActivityViewModelSchema(BaseModel):
    activity_type: Optional[str] = Field(None, alias="ACTIVITY_TYPE")
    activity_title: Optional[str] = Field(None, alias="ACTIVITY_TITLE")
    activity_dt: Optional[datetime] = Field(None, alias="ACTIVITY_DT")
    requested_from: Optional[str] = Field(None, alias="REQUESTED_FROM")

    class Config:
        populate_by_name = True
