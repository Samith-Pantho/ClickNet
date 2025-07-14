from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class CustomerRegistrationSchema(BaseModel):
    user_id: Optional[str] = Field(None, title="User ID")
    customer_title: str = Field(..., title="Customer Title")
    customer_id: str = Field(..., title="Customer ID")
    tax_id: str = Field(..., title="TAX ID")
    phone_number: str = Field(..., title="Phone Number")
    birth_date: datetime = Field(..., title="Phone Number")
    email: Optional[EmailStr] = Field(None, title="Email") 
    remark: Optional[str] = Field(None, title="Remark")
    OTP: Optional[str] = Field(None, title="OTP")
    OTP_verify_channel: Optional[str] = Field(None, title="OTP Verification Channel")
    
    class Config:
        from_attributes = True  # Required to convert SQLAlchemy model -> Pydantic schema
