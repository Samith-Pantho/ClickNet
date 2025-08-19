from typing import Optional
from pydantic import BaseModel

class InitializeRequestviewModelShema(BaseModel):
    product_code: str
    branch_code: str
    phone_number: str
    email_address: Optional[str]
