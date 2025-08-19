from typing import Optional
from pydantic import BaseModel

class VerifiyMobileRequestviewModelShema(BaseModel):
    phone_number: str
    code: str
