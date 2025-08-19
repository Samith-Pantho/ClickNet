from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DiditFaceMatchesSchema(BaseModel):
    id: Optional[int] = Field(None, alias="id")
    session_id: str = Field(..., alias="session_id")
    score: Optional[float] = Field(None, alias="score")
    source_image: Optional[str] = Field(None, alias="source_image")
    source_image_session_id: Optional[str] = Field(None, alias="source_image_session_id")
    status: Optional[str] = Field(None, alias="status")
    target_image: Optional[str] = Field(None, alias="target_image")
    warnings: Optional[Dict[str, Any]] = Field(None, alias="warnings")

    class Config:
        populate_by_name = True
