from pydantic import BaseModel
from typing import Optional


class CBSBranchDetailsSchema(BaseModel):
    branch_code: Optional[str]
    branch_name: Optional[str]
    lat: Optional[float]
    lng: Optional[float]

    class Config:
        from_attributes = True