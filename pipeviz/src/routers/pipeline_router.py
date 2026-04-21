"""
Pipeline router module.
This will contain all endpoints related to the pipeline.
Authors:
    - Laxminarayana Vadnala <lvadnala@nd.edu>
"""

from tracemalloc import reset_peak

from fastapi import APIRouter, HTTPException, status

from src.enum_vault.pipeline_enums import DataHazardTypes, PipelineTypes
from src.enum_vault.workflow_enums import SupportedProgrammingLanguagesEnum
from src.models.pipeline_router_models import (
    DataHazardResponseModel,
    LanguageResponseModel,
    SupportedPipelineResponseModel,
)

router = APIRouter(tags=["Pipeline Routes"], prefix="/api")


@router.get("/pipelineSupportedLanguages", response_model=LanguageResponseModel)
async def get_pipeline_supported_languages():
    try:
        languages = [lang.value for lang in SupportedProgrammingLanguagesEnum]
        response = LanguageResponseModel(languages=languages)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/supportedPipelines", response_model=SupportedPipelineResponseModel)
async def get_supported_pipelines():
    try:
        return SupportedPipelineResponseModel(
            supported_pipelines=[pipeline.value for pipeline in PipelineTypes]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/supportedDataHazards", response_model=DataHazardResponseModel)
async def get_supported_data_hazards():
    try:
        return DataHazardResponseModel(
            supported_data_hazards=[hazard.value for hazard in DataHazardTypes]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/get_code")
async def get_code():
    try:
        return {"code": ""}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/pipelines")
async def get_pipelines():
    try:
        return {"pipelines": []}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
