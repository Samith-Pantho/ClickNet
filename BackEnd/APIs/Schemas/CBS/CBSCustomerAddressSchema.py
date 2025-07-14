from pydantic import BaseModel, Field
from typing import Optional

class CBSCustomerAddressSchema(BaseModel):
    id: int = Field(..., title="ID")
    customer_id: str = Field(..., title="Customer ID")
    type: Optional[str] = Field(None, title="Address Type")
    line_1: Optional[str] = Field(None, title="Address Line 1")
    line_2: Optional[str] = Field(None, title="Address Line 2")
    line_3: Optional[str] = Field(None, title="Address Line 3")
    line_4: Optional[str] = Field(None, title="Address Line 4")
    city: Optional[str] = Field(None, title="City")
    state_code: Optional[str] = Field(None, title="State Code")
    zip_code: Optional[str] = Field(None, title="Zip Code")
    country_code: Optional[str] = Field(None, title="Country Code")

    class Config:
        from_attributes = True