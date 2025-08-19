from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerRegistrationSchema(BaseModel):
    tracking_id: str = Field(..., alias="TRACKING_ID")
    
    # Personal Information
    name: Optional[str] = Field(None, alias="NAME")
    title: Optional[str] = Field(None, alias="TITLE")
    first_name: Optional[str] = Field(None, alias="FIRST_NAME")
    middle_name: Optional[str] = Field(None, alias="MIDDLE_NAME")
    last_name: Optional[str] = Field(None, alias="LAST_NAME")
    suffix: Optional[str] = Field(None, alias="SUFFIX")
    birth_date: Optional[datetime] = Field(None, alias="BIRTH_DATE")
    tax_id: Optional[str] = Field(None, alias="TAX_ID")
    tax_id_type: Optional[str] = Field(None, alias="TAX_ID_TYPE")
    is_tax_id_verified: Optional[bool] = Field(None, alias="IS_TAX_ID_VERIFIED")
    verification_session_id: Optional[str] = Field(None, alias="VERIFICATION_SESSION_ID")
    
    # Address Information
    address_type: Optional[str] = Field(None, alias="ADDRESS_TYPE")
    line_1: Optional[str] = Field(None, alias="LINE_1")
    line_2: Optional[str] = Field(None, alias="LINE_2")
    line_3: Optional[str] = Field(None, alias="LINE_3")
    line_4: Optional[str] = Field(None, alias="LINE_4")
    city: Optional[str] = Field(None, alias="CITY")
    state_code: Optional[str] = Field(None, alias="STATE_CODE")
    zipcode: Optional[str] = Field(None, alias="ZIPCODE")
    country_code: Optional[str] = Field(None, alias="COUNTRY_CODE")
    
    # Contact Information
    email_address: Optional[str] = Field(None, alias="EMAIL_ADDRESS")
    phone_number: str = Field(..., alias="PHONE_NUMBER")
    
    # Account Information
    product_code: str = Field(..., alias="PRODUCT_CODE")
    branch_code: Optional[str] = Field(None, alias="BRANCH_CODE")
    customer_id: Optional[str] = Field(None, alias="CUSTOMER_ID")
    account_number: Optional[str] = Field(None, alias="ACCOUNT_NUMBER")
    
    # Additional fields
    create_by: Optional[str] = Field(None, alias="CREATE_BY")
    create_dt: Optional[datetime] = Field(None, alias="CREATE_DT")
    status: Optional[str] = Field(None, alias="STATUS")
    reject_reason: Optional[str] = Field(None, alias="REJECT_REASON")

    class Config:
        populate_by_name = True