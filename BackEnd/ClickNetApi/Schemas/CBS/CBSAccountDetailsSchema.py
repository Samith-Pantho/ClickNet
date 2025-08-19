from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CBSAccountDetailsSchema(BaseModel):
    account_number: str = Field(..., title="Account Number")
    product_category: Optional[str] = Field(None, title="Product Category")
    product_type: Optional[str] = Field(None, title="Product Type")
    product_name: Optional[str] = Field(None, title="Product Name")
    status: Optional[str] = Field(None, title="Status")
    relationship: Optional[str] = Field(None, title="Relationship")
    branch_code: Optional[str] = Field(None, title="Branch Code")
    opened_date: Optional[datetime] = Field(None, title="Opened Date")
    maturity_date: Optional[datetime] = Field(None, title="Maturity Date")

    class Config:
        from_attributes = True