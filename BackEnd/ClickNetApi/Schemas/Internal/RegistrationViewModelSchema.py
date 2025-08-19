from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class RegistrationViewModelSchema(BaseModel):
    user_id: str
    customer_title: str
    customer_id: str 
    tax_id: str 
    phone_number: str 
    birth_date: datetime 
    email: Optional[EmailStr] 
    remark: Optional[str] 
    OTP: Optional[str] 
    OTP_verify_channel: str
    captcha_token: Optional[str]
    
    class Config:
        from_attributes = True  # Required to convert SQLAlchemy model -> Pydantic schema
