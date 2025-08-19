from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerChatSessionSchema(BaseModel):
    session_id: Optional[int] = Field(None, alias="SESSION_ID")
    user_id: str = Field(..., alias="USER_ID")
    started_at: Optional[datetime] = Field(default_factory=datetime.now, alias="STARTED_AT")
    
    class Config:
        populate_by_name = True
