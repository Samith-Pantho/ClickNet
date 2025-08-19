from pydantic import BaseModel
from typing import Optional

class AddMoneyViewModelSchema(BaseModel):
    ToAccountNo: str
    ReceiverName: str
    Amount: float
    Currency: str
    Vendor: str

    class Config:
        from_attributes = True 