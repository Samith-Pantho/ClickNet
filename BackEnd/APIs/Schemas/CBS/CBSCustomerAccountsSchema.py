from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CBSCustomerAccountsSchema(BaseModel):
    account_number: str = Field(..., title="Account Number")
    branch_code: Optional[str] = Field(None, title="Branch Code")
    product_category: Optional[str] = Field(None, title="Product Category")
    product_type: Optional[str] = Field(None, title="Product Type")
    product_name: Optional[str] = Field(None, title="Product Name")

    class Config:
        from_attributes = True