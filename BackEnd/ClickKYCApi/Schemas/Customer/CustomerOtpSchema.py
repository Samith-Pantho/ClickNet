from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerOtpSchema(BaseModel):
    sl: Optional[int] = Field(None, alias="SL")
    db_svr_dt: Optional[datetime] = Field(None, alias="DB_SVR_DT")
    phone_number: Optional[str] = Field(None, alias="PHONE_NUMBER")
    phone_message: Optional[str] = Field(None, alias="PHONE_MESSAGE")
    phone_otp: Optional[str] = Field(None, alias="PHONE_OTP")
    phone_otp_expired_at: Optional[datetime] = Field(None, alias="PHONE_OTP_EXPIRED_AT")
    phone_otp_verified_at: Optional[datetime] = Field(None, alias="PHONE_OTP_VERIFIED_AT")
    phone_sent_at: Optional[datetime] = Field(None, alias="PHONE_SENT_AT")
    phone_otp_remarks: Optional[str] = Field("PENDING", alias="PHONE_OTP_REMARKS")
    email_address: Optional[str] = Field(None, alias="EMAIL_ADDRESS")
    email_message: Optional[str] = Field(None, alias="EMAIL_MESSAGE")
    email_otp: Optional[str] = Field(None, alias="EMAIL_OTP")
    email_otp_expired_at: Optional[datetime] = Field(None, alias="EMAIL_OTP_EXPIRED_AT")
    email_otp_verified_at: Optional[datetime] = Field(None, alias="EMAIL_OTP_VERIFIED_AT")
    email_sent_at: Optional[datetime] = Field(None, alias="EMAIL_SENT_AT")
    email_otp_remarks: Optional[str] = Field("PENDING", alias="EMAIL_OTP_REMARKS")
    ip_address: Optional[str] = Field("::1", alias="IP_ADDRESS")

    class Config:
        populate_by_name = True