from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CBSAccountFullDetailsSchema(BaseModel):
    account_number: str = Field(..., title="Account Number")
    customer_id: str = Field(..., title="Customer ID")
    product_category: Optional[str] = Field(None, title="Product Category")
    product_type: Optional[str] = Field(None, title="Product Type")
    product_name: Optional[str] = Field(None, title="Product Name")
    status: Optional[str] = Field(None, title="Status")
    relationship: Optional[str] = Field(None, title="Relationship")
    branch_code: Optional[str] = Field(None, title="Branch Code")
    opened_date: Optional[datetime] = Field(None, title="Opened Date")
    maturity_date: Optional[datetime] = Field(None, title="Maturity Date")
    original_balance: Optional[int] = Field(None, title="Original Balance")
    current_balance: Optional[int] = Field(None, title="Current Balance")
    available_balance: Optional[int] = Field(None, title="Available Balance")
    payment_frequency: Optional[str] = Field(None, title="Payment Frequency")
    payment_min_amount: Optional[int] = Field(None, title="Payment Min Amount")
    payment_max_amount: Optional[int] = Field(None, title="Payment Max Amount")
    interest_rate: Optional[float] = Field(None, title="Interest Rate")
    secured: Optional[bool] = Field(None, title="Secured")
    daily_no_of_payments: Optional[int] = Field(None, title="Daily Number of Payments")

    class Config:
        from_attributes = True