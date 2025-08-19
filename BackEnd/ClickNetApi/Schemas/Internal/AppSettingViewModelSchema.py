from pydantic import BaseModel

class AppSettingViewModelSchema(BaseModel):
    KEY: str
    VALUE: str