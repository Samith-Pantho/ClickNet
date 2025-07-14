from pydantic import BaseModel, Field
from typing import Optional

class CBSCustomerPhoneSchema(BaseModel):
    id: int = Field(..., title="ID")
    customer_id: str = Field(..., title="Customer ID")
    type: Optional[str] = Field(None, title="Phone Type")
    number: Optional[str] = Field(None, title="Phone Number")

    class Config:
        from_attributes = True