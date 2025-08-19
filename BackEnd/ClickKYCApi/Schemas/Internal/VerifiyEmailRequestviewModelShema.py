from typing import Optional
from pydantic import BaseModel

class VerifiyEmailRequestviewModelShema(BaseModel):
    email_address: str
    code: str
