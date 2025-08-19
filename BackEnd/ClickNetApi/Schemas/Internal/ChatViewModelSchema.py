from typing import Optional

from pydantic import BaseModel


class ChatRequestViewModelSchema(BaseModel):
    session_id: Optional[int] = None
    message: str

class ChatResponseViewModelSchema(BaseModel):
    session_id: int
    response: str
