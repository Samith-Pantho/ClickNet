from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CBSTransactionHistorySchema(BaseModel):
    name: str 
    trans_date: datetime 
    trans_mode: str 
    dr_cr: str 
    trans_id: str
    narration: str 
    purpose: Optional[str] 
    amount: float 
    currency_nm: str 

    class Config:
        from_attributes = True
