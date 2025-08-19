from typing import Optional
from pydantic import BaseModel

class ProductViewModelSchema(BaseModel):
    product_code: str
    product_name: str
    product_type: str
    description: Optional[str]