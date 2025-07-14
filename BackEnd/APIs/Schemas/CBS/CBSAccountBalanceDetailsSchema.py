from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CBSAccountBalanceDetailsSchema(BaseModel):
    original_balance: Optional[int] = Field(None, title="Original Balance")
    current_balance: Optional[int] = Field(None, title="Current Balance")
    available_balance: Optional[int] = Field(None, title="Available Balance")
    interest_rate: Optional[float] = Field(None, title="Interest Rate")

    class Config:
        from_attributes = True