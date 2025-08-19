from typing import Optional

from pydantic import BaseModel


class ComplaintViewModelSchema(BaseModel):
    category: str
    description: str

