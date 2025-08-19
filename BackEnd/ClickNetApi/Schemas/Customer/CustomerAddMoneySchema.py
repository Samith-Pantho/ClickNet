from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerAddMoneySchema(BaseModel):
    id: Optional[int] = Field(None, alias="ID")
    user_id: str = Field(..., alias="USER_ID")
    session_id: str = Field(..., alias="SESSION_ID")
    receiver_no: str = Field(..., alias="RECEIVER_NO")
    receiver_name: str = Field(..., alias="RECEIVER_NAME")
    payment_via: str = Field(..., alias="PAYMENT_VIA")
    amount_in_cent: int = Field(..., alias="AMOUNT_IN_CENT")
    currency: str = Field(..., alias="CURRENCY")
    payment_id: str = Field(..., alias="PAYMENT_ID")
    create_dt: datetime = Field(..., alias="CREATE_DT")
    success_secret_key: str = Field(..., alias="SUCCESS_SECRET_KEY")
    failed_secret_key: str = Field(..., alias="FAILED_SECRET_KEY")
    success_or_failed_process_dt: Optional[datetime] = Field(None, alias="SUCCESS_OR_FAILED_PROCESS_DT")
    payment_status: Optional[str] = Field(None, alias="PAYMENT_STATUS")
    update_dt: Optional[datetime] = Field(None, alias="UPDATE_DT")
    cbs_trx_id: Optional[str] = Field(None, alias="CBS_TRX_ID")
    trx_dt: Optional[datetime] = Field(None, alias="TRX_DT")

    class Config:
        populate_by_name = True
