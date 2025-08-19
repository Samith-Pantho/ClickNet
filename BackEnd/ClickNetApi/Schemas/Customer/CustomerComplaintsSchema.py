from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerComplaintsSchema(BaseModel):
    id: Optional[int] = Field(None, alias="ID")
    user_id: str = Field(..., alias="USER_ID")
    category: str = Field(..., alias="CATEGORY")
    description: str = Field(..., alias="DESCRIPTION")
    status: Optional[str] = Field("OPEN", alias="STATUS")
    response: Optional[str] = Field(None, alias="RESPONSE")
    created_at: Optional[datetime] = Field(None, alias="CREATED_AT")
    updated_at: Optional[datetime] = Field(None, alias="UPDATED_AT")

    class Config:
        populate_by_name = True
