from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DiditWarningsSchema(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    session_id: str = Field(..., alias="session_id")
    feature: Optional[str] = Field(None, alias="feature")
    log_type: Optional[str] = Field(None, alias="log_type")
    short_description: Optional[str] = Field(None, alias="short_description")
    long_description: Optional[str] = Field(None, alias="long_description")
    risk: Optional[str] = Field(None, alias="risk")
    additional_data: Optional[Dict[str, Any]] = Field(None, alias="additional_data")
    created_at: Optional[datetime] = Field(None, alias="created_at")

    class Config:
        populate_by_name = True