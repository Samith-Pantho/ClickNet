from pydantic import BaseModel
from typing import Optional

class ChangePasswordViewModelSchema(BaseModel):
    UserID: str
    OldPassword: str
    NewPassword: str
    ConfirmNewPassword: str

    class Config:
        from_attributes = True  # Enables compatibility with ORM models
