from pydantic import BaseModel, Field
from typing import Optional

class SystemAdvertisementsSchema(BaseModel):
    sl: Optional[int] = Field(None, alias="SL")
    title: Optional[str] = Field(None, alias="TITLE")
    image_url: Optional[str] = Field(None, alias="IMAGE_URL")
    target_url: Optional[str] = Field(None, alias="TARGET_URL")
    status: Optional[bool] = Field(None, alias="STATUS")

    class Config:
        populate_by_name = True 