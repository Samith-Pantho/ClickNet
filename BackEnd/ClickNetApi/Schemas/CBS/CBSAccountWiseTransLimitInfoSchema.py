from pydantic import BaseModel, Field
from typing import Optional


class CBSAccountWiseTransLimitInfoSchema(BaseModel):
    payment_frequency: Optional[str] = Field(None, title="Payment Frequency Code (e.g., D/M)")
    payment_min_amount: Optional[float] = Field(None, title="Minimum Payment Amount")
    payment_max_amount: Optional[float] = Field(None, title="Maximum Payment Amount")
    daily_no_of_payments: Optional[int] = Field(None, title="Maximum Daily Number of Payments")
    today_total_amount: Optional[float] = Field(None, title="Total Amount Debited Today")
    today_total_transactions: Optional[int] = Field(None, title="Total Number of Transactions Today")

    class Config:
        from_attributes = True
