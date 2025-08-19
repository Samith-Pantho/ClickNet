from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class CustomerOtpSchema(BaseModel):
    otp_sl: Optional[int] = Field(None, alias="OTP_SL")
    user_id: str = Field(..., alias="USER_ID")
    cust_id: str = Field(..., alias="CUST_ID")
    dv_svr_dt: Optional[datetime] = Field(None, alias="DB_SVR_DT")
    phone_number: Optional[str] = Field("", alias="PHONE_NUMBER")
    email_address: Optional[str] = Field("", alias="EMAIL_ADDRESS")
    verification_channel: Optional[str] = Field("EMAIL", alias="VERIFICATION_CHANNEL")
    message: Optional[str] = Field(None, alias="MESSAGE")
    otp: Optional[str] = Field(None, alias="OTP")
    otp_expired_at: Optional[datetime] = Field(None, alias="OTP_EXPIRED_AT")
    otp_verified_at: Optional[datetime] = Field(None, alias="OTP_VERIFIED_AT")
    sent_at: Optional[datetime] = Field(None, alias="SENT_AT")
    from_account_no: str = Field("00000000000", alias="FROM_ACCOUNT_NO")
    from_branch_id: str = Field("0000", alias="FROM_BRANCH_ID")
    to_account_no: str = Field("00000000000", alias="TO_ACCOUNT_NO")
    to_branch_id: str = Field("0000", alias="TO_BRANCH_ID")
    to_bank_id: Optional[str] = Field("0000", alias="TO_BANK_ID")
    to_routing_numb: Optional[str] = Field("000000000", alias="TO_ROUTING_NUMB")
    ip_address: str = Field("::1", alias="IP_ADDRESS")
    amount_ccy: Optional[Decimal] = Field(Decimal("0.0"), alias="AMOUNT_CCY")
    amount_lcy: Optional[Decimal] = Field(Decimal("0.0"), alias="AMOUNT_LCY")
    transfer_type: str = Field("0", alias="TRANSFER_TYPE")
    purpose_of_transaction: Optional[str] = Field(None, alias="PURPOSE_OF_TRANSACTION")
    receiver_id: Optional[str] = Field(None, alias="RECEIVER_ID")
    receiver_nm: Optional[str] = Field(None, alias="RECEIVER_NM")
    remarks: Optional[str] = Field(None, alias="REMARKS")

    class Config:
        populate_by_name = True
