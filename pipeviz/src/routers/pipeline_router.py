"""
Pipeline router module.
This will contain all endpoints related to the pipeline.
Authors:
    - Laxminarayana Vadnala <lvadnala@nd.edu>
"""

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from src.enum_vault.pipeline_enums import HazardType, PipelineStage, PipelineTypes
from src.enum_vault.workflow_enums import SupportedProgrammingLanguagesEnum
from src.models.pipeline_router_models import (
    DataHazardResponseModel,
    LanguageResponseModel,
    SupportedPipelineResponseModel,
)
from src.pipeline.pipeviz_workflow import PipeVizWorkflow
from src.pipeline.simulate_pipeline import PipelineSimulator
from src.pipeline.utils import extract_function_assembly

router = APIRouter(tags=["Pipeline Routes"], prefix="/api")


@router.get("/pipeline_supported_languages", response_model=LanguageResponseModel)
async def get_pipeline_supported_languages():
    try:
        languages = [lang.value for lang in SupportedProgrammingLanguagesEnum]
        response = LanguageResponseModel(languages=languages)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/supported_pipelines", response_model=SupportedPipelineResponseModel)
async def get_supported_pipelines():
    try:
        return SupportedPipelineResponseModel(
            supported_pipelines=[pipeline.value for pipeline in PipelineTypes]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/supported_hazards", response_model=DataHazardResponseModel)
async def get_supported_data_hazards():
    try:
        return DataHazardResponseModel(
            supported_data_hazards=[hazard.value for hazard in HazardType]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/get_code")
async def get_code():
    try:
        return {"code": ""}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulate_pipelines", response_model=None)
async def simulate_pipelines(
    code: str,
    language: SupportedProgrammingLanguagesEnum,
    mock_exsisting_code: bool = False,
    function_name: str = "main",
    pipeline_type: PipelineTypes = PipelineTypes.STATIC,
    cycle_weights: dict[str, int] = {i.name.lower(): 1 for i in PipelineStage},
):
    try:
        # validate the code and generate assembly code
        workflow = PipeVizWorkflow(language)

        if mock_exsisting_code:
            result, asm_path = workflow.generate_asembly_code(
                workflow._paths.rust_mock_path
            )
        else:
            # we are not running mock code, so we use the provided code
            if language == SupportedProgrammingLanguagesEnum.RUST:
                code_path = workflow.run_path / "main.rs"
            elif language == SupportedProgrammingLanguagesEnum.C:
                code_path = workflow.run_path / "main.c"
            elif language == SupportedProgrammingLanguagesEnum.CPP:
                code_path = workflow.run_path / "main.cpp"

            with open(code_path, "w") as f:
                f.write(code)

            result, asm_path = workflow.generate_asembly_code(code_path)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate assembly code: {asm_path}",
            )

        # read the assembly code
        with open(asm_path, "r") as f:
            asm_code = f.read()

        # Extract just the function (only real instruction lines)
        function_lines = extract_function_assembly(asm_code, function_name)

        if not function_lines:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Function '{function_name}' not found in assembly code.",
            )

        logger.info("Analyzing Fibonacci function...")

        # Simulate with forwarding
        logger.info("SIMULATION WITH FORWARDING")
        logger.info("=" * 100)
        sim_forward = PipelineSimulator(enable_forwarding=True)
        sim_forward.load_instructions(function_lines)
        sim_forward.simulate()
        sim_forward.print_simulation()
        sim_forward.export_csv("sim_forward.csv")

        # Simulate without forwarding
        logger.info("SIMULATION WITHOUT FORWARDING")
        logger.info("=" * 100)
        sim_no_forward = PipelineSimulator(enable_forwarding=False)
        sim_no_forward.load_instructions(function_lines)
        sim_no_forward.simulate()
        sim_no_forward.print_simulation()
        sim_no_forward.export_csv("sim_no_forward.csv")

        return {"pipelines": []}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
