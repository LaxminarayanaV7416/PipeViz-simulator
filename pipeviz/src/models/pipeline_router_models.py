from pydantic import BaseModel


class LanguageResponseModel(BaseModel):
    languages: list[str]
