from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CBSCustomerInfoSchema(BaseModel):
    customer_id: str = Field(..., title="Customer ID")
    type: Optional[str] = Field(None, title="Customer Type")
    name: Optional[str] = Field(None, title="Full Name")
    title: Optional[str] = Field(None, title="Title")
    first_name: Optional[str] = Field(None, title="First Name")
    middle_name: Optional[str] = Field(None, title="Middle Name")
    last_name: Optional[str] = Field(None, title="Last Name")
    suffix: Optional[str] = Field(None, title="Suffix")
    birth_date: Optional[datetime] = Field(None, title="Birth Date")
    formation_date: Optional[datetime] = Field(None, title="Formation Date")
    tax_id: Optional[str] = Field(None, title="Tax ID")
    tax_id_type: Optional[str] = Field(None, title="Tax ID Type")
    branch_code: Optional[str] = Field(None, title="Branch Code")

    class Config:
        from_attributes = True