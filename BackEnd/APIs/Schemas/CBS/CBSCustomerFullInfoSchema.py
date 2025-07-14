from typing import List
from pydantic import BaseModel
from  .CBSCustomerInfoSchema import CBSCustomerInfoSchema
from  .CBSCustomerAddressSchema import CBSCustomerAddressSchema
from  .CBSCustomerEmailSchema import CBSCustomerEmailSchema
from  .CBSCustomerPhoneSchema import CBSCustomerPhoneSchema

class CBSCustomerFullInfoSchema(BaseModel):
    customer: CBSCustomerInfoSchema
    addresses: List[CBSCustomerAddressSchema] = []
    emails: List[CBSCustomerEmailSchema] = []
    phones: List[CBSCustomerPhoneSchema] = []

    class Config:
        from_attributes = True