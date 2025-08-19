from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerPhotoSchema(BaseModel):
    user_id: Optional[str] = Field(None, alias="USER_ID")
    photo_path: Optional[str] = Field(None, alias="PHOTO_PATH")
    create_by: Optional[str] = Field(None, alias="CREATE_BY")
    create_at: Optional[datetime] = Field(None, alias="CREATE_AT")

    class Config:
        populate_by_name = True
