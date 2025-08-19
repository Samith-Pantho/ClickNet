from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DiditLivenessSchema(BaseModel):
    session_id: str = Field(..., alias="session_id")
    age_estimation: Optional[float] = Field(None, alias="age_estimation")
    method: Optional[str] = Field(None, alias="method")
    reference_image: Optional[str] = Field(None, alias="reference_image")
    score: Optional[float] = Field(None, alias="score")
    status: Optional[str] = Field(None, alias="status")
    video_url: Optional[str] = Field(None, alias="video_url")
    warnings: Optional[Dict[str, Any]] = Field(None, alias="warnings")

    class Config:
        populate_by_name = True
