from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerChatMessageSchema(BaseModel):
    id: Optional[int] = Field(None, alias="ID")
    session_id: int = Field(..., alias="SESSION_ID")
    role: str = Field(..., alias="ROLE")  # "user" or "assistant"
    message: str = Field(..., alias="MESSAGE")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, alias="CREATED_AT")
   
    class Config:
        populate_by_name = True
