from pydantic import BaseModel
from typing import Optional
from datetime import date

class SystemActivitySchema(BaseModel):
    Type: Optional[str]
    Title: Optional[str]
    Details: Optional[str]
    IpAddress: Optional[str]
    UserType: Optional[str]
    User_Id: Optional[str]

    class Config:
        from_attributes = True  # Allows use with SQLAlchemy models (ORM mode)
