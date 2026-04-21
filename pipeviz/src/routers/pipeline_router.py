"""
Pipeline router module.
This will contain all endpoints related to the pipeline.
Authors:
    - Laxminarayana Vadnala <lvadnala@nd.edu>
"""

from fastapi import APIRouter, HTTPException, status

from src.enum_vault.workflow_enums import SupportedProgrammingLanguagesEnum
from src.models.pipeline_router_models import LanguageResponseModel

router = APIRouter(tags=["Pipeline Routes"], prefix="/api")


@router.get("/pipelineSupportedLanguages", response_model=LanguageResponseModel)
async def get_pipeline_supported_languages():
    try:
        languages = [lang.value for lang in SupportedProgrammingLanguagesEnum]
        response = LanguageResponseModel(languages=languages)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/pipelines")
async def get_pipelines():
    try:
        return {"pipelines": []}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
