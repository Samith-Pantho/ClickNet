from pydantic import BaseModel, Field
from typing import Optional

class CBSCustomerEmailSchema(BaseModel):
    id: int = Field(..., title="ID")
    customer_id: str = Field(..., title="Customer ID")
    type: Optional[str] = Field(None, title="Email Type")
    address: Optional[str] = Field(None, title="Email Address")

    class Config:
        from_attributes = True