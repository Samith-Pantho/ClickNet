from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DiditSessionsSchema(BaseModel):
    session_id: str = Field(..., alias="session_id")
    session_number: Optional[int] = Field(None, alias="session_number")
    session_token: Optional[str] = Field(None, alias="session_token")
    url: Optional[str] = Field(None, alias="url")
    vendor_data: Optional[str] = Field(None, alias="vendor_data")
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    status: Optional[str] = Field(None, alias="status")
    callback: Optional[str] = Field(None, alias="callback")
    workflow_id: Optional[str] = Field(None, alias="workflow_id")
    created_at: Optional[datetime] = Field(None, alias="created_at")
    updated_at: Optional[datetime] = Field(None, alias="updated_at")

    class Config:
        populate_by_name = True
