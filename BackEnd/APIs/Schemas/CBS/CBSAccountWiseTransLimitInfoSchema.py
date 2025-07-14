from pydantic import BaseModel
from typing import Optional

class CBSAccountWiseTransLimitInfoSchema(BaseModel):
    payment_frequency: Optional[str]
    payment_min_amount: Optional[int]
    payment_max_amount: Optional[int]
    daily_no_of_payments: Optional[int]

    class Config:
        from_attributes = True