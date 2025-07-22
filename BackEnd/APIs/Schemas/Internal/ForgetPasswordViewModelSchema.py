from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class ForgetPasswordViewModelSchema(BaseModel):
    UserID:str
    Newpassword:Optional[str] 
    ConfirmNewPassword:Optional[str] 
    CustomerID: str
    TaxID: str
    BirthDate: datetime
    Phone: str
    Email: Optional[EmailStr]
    OTP: Optional[str] 
    OTP_verify_channel: str

    class Config:
        from_attributes = True  # Enables compatibility with ORM models
