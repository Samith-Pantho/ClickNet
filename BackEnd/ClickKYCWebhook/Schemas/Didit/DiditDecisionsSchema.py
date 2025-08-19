from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DiditDecisionsSchema(BaseModel):
    session_id: str = Field(..., alias="session_id")
    aml: Optional[str] = Field(None, alias="aml")
    callback: Optional[str] = Field(None, alias="callback")
    contact_details: Optional[str] = Field(None, alias="contact_details")
    created_at: Optional[datetime] = Field(None, alias="created_at")
    database_validation: Optional[str] = Field(None, alias="database_validation")
    expected_details: Optional[str] = Field(None, alias="expected_details")
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    nfc: Optional[str] = Field(None, alias="nfc")
    phone: Optional[str] = Field(None, alias="phone")
    poa: Optional[str] = Field(None, alias="poa")
    reviews: Optional[Dict[str, Any]] = Field(None, alias="reviews")
    status: Optional[str] = Field(None, alias="status")
    vendor_data: Optional[str] = Field(None, alias="vendor_data")
    workflow_id: Optional[str] = Field(None, alias="workflow_id")
    session_url: Optional[str] = Field(None, alias="session_url")
    session_number: Optional[int] = Field(None, alias="session_number")

    class Config:
        populate_by_name = True
