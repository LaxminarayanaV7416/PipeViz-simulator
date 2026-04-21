from pydantic import BaseModel


class LanguageResponseModel(BaseModel):
    languages: list[str]


class SupportedPipelineResponseModel(BaseModel):
    supported_pipelines: list[str]
    

class DataHazardResponseModel(BaseModel):
    supported_data_hazards: list[str]