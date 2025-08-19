from pydantic import BaseModel
from typing import Optional

class NotificationViewModelSchema(BaseModel):
    Delivery_channel: str
    Phone: Optional[str]
    Email: Optional[str]
    Title: Optional[str]
    Message: Optional[str]

    class Config:
        from_attributes = True  # Enables compatibility with ORM models
