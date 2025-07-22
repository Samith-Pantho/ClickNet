from pydantic import BaseModel
from typing import Optional

class LoginViewModelSchema(BaseModel):
    UserID: str
    Password: str
    IPAddress: str
    OTP: Optional[str]
    OTP_verify_channel: Optional[str]

    class Config:
        from_attributes = True  # Enables compatibility with ORM models
