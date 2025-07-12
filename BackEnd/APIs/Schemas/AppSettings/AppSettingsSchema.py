from pydantic import BaseModel, Field
from typing import Optional

class AppSettingsSchema(BaseModel):
    Key: str = Field(..., title="Key")
    Value: str = Field(..., title="Value")
    Description: Optional[str] = Field(None, title="Description")
    Privacylevel: Optional[str] = Field(None, title="Privacy Level")
    
    class Config:
        from_attributes = True  # Required to convert SQLAlchemy model -> Pydantic schema