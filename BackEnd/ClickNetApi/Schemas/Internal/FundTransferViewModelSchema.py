from pydantic import BaseModel
from typing import Optional

class FundTransferViewModelSchema(BaseModel):
    FromAccount: str
    SenderName: str
    ToAccount: str
    ReceiverName: str
    Pourpose: str
    Amount: str
    Currency: str
    OTP: Optional[str]
    OTP_verify_channel: Optional[str]

    class Config:
        from_attributes = True  # Enables compatibility with ORM models
