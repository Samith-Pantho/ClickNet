from pydantic import BaseModel
from typing import Optional

class NotificationViewModelSchema(BaseModel):
    Title: Optional[str]
    Message: Optional[str]
    Phone: Optional[str]
    Email: Optional[str]
    Delivery_channel: Optional[str]

    class Config:
        from_attributes = True  # Enables compatibility with ORM models
