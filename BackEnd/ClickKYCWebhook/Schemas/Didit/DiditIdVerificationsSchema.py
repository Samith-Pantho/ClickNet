from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DiditIdVerificationsSchema(BaseModel):
    session_id: str = Field(..., alias="session_id")
    address: Optional[str] = Field(None, alias="address")
    age: Optional[int] = Field(None, alias="age")
    back_image: Optional[str] = Field(None, alias="back_image")
    back_video: Optional[str] = Field(None, alias="back_video")
    date_of_birth: Optional[datetime] = Field(None, alias="date_of_birth")
    date_of_issue: Optional[datetime] = Field(None, alias="date_of_issue")
    document_number: Optional[str] = Field(None, alias="document_number")
    document_type: Optional[str] = Field(None, alias="document_type")
    expiration_date: Optional[datetime] = Field(None, alias="expiration_date")
    extra_fields: Optional[Dict[str, Any]] = Field(None, alias="extra_fields")
    extra_files: Optional[Dict[str, Any]] = Field(None, alias="extra_files")
    first_name: Optional[str] = Field(None, alias="first_name")
    formatted_address: Optional[str] = Field(None, alias="formatted_address")
    front_image: Optional[str] = Field(None, alias="front_image")
    front_video: Optional[str] = Field(None, alias="front_video")
    full_back_image: Optional[str] = Field(None, alias="full_back_image")
    full_front_image: Optional[str] = Field(None, alias="full_front_image")
    full_name: Optional[str] = Field(None, alias="full_name")
    gender: Optional[str] = Field(None, alias="gender")
    issuing_state: Optional[str] = Field(None, alias="issuing_state")
    issuing_state_name: Optional[str] = Field(None, alias="issuing_state_name")
    last_name: Optional[str] = Field(None, alias="last_name")
    marital_status: Optional[str] = Field(None, alias="marital_status")
    nationality: Optional[str] = Field(None, alias="nationality")
    parsed_address: Optional[str] = Field(None, alias="parsed_address")
    personal_number: Optional[str] = Field(None, alias="personal_number")
    place_of_birth: Optional[str] = Field(None, alias="place_of_birth")
    portrait_image: Optional[str] = Field(None, alias="portrait_image")
    status: Optional[str] = Field(None, alias="status")
    warnings: Optional[Dict[str, Any]] = Field(None, alias="warnings")

    class Config:
        populate_by_name = True
