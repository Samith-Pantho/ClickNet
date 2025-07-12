from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class CustomerRegistrationSchema(BaseModel):
    id: int = Field(..., title="ID")
    branch_id: str = Field(..., title="Branch ID")
    branch_nm: str = Field(..., title="Branch Name")
    account_no: str = Field(..., title="Account No")
    accoun_ttitle: str = Field(..., title="Accoun Ttitle")
    customer_id: str = Field(..., title="Customer ID")
    hardware_token: Optional[str] = Field(None, title="Hardware Token")
    authentication_type: str = Field(..., title="Authentication Type")
    phone_number: str = Field(..., title="Phone Number")
    email: EmailStr = Field(..., title="Email")  # Ensures valid email format

    imei1: Optional[str] = Field(None, title="IP / IMEI - 1")
    imei2: Optional[str] = Field(None, title="IP / IMEI - 2")
    remark: Optional[str] = Field(None, title="Remark")

    status: int = Field(..., title="Status")
    process_flag: bool = Field(..., title="Process Flag")
    process_by: Optional[str] = Field(None, title="Process By")
    process_dt: Optional[datetime] = Field(None, title="Process Date")
    create_by: str = Field(..., title="Create By")
    create_dt: datetime = Field(..., title="Create Date")
    update_dt: Optional[datetime] = Field(None, title="Update Date")
    update_by: Optional[str] = Field(None, title="Update By")
    is_checked: bool = Field(..., title="Is Checked")
    check_by: Optional[str] = Field(None, title="Check By")
    check_dt: Optional[datetime] = Field(None, title="Check Date")
    is_authorized: bool = Field(..., title="Is Authorized")
    authorize_by: Optional[str] = Field(None, title="Authorize By")
    authorize_dt: Optional[datetime] = Field(None, title="Authorize Date")
    
    class Config:
        from_attributes = True  # Required to convert SQLAlchemy model -> Pydantic schema
