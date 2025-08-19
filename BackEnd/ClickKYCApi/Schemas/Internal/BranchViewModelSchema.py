from typing import Optional
from pydantic import BaseModel

class BranchViewModelSchema(BaseModel):
    branch_code: Optional[str]
    branch_name: Optional[str]