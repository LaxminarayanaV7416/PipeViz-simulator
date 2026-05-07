"""
Pipeline router module.
This will contain all endpoints related to the pipeline.
Authors:
    - Laxminarayana Vadnala <lvadnala@nd.edu>
"""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException, status
from loguru import logger

from src.enum_vault.pipeline_enums import (
    DynamicInOrderStages,
    HazardType,
    InOrderSuperscalarStages,
    OutOfOrderStages,
    PipelineTypes,
    ScoreboardStages,
    StaticInOrderStages,
    TomasuloStages,
    VLIWStages,
)
from src.enum_vault.workflow_enums import (
    CompilerOptimizationsEnum,
    SupportedProgrammingLanguagesEnum,
    WorkflowPaths,
)
from src.models.pipeline_router_models import (
    DataHazardResponseModel,
    LanguageResponseModel,
    SupportedPipelineResponseModel,
)
from src.pipeline.pipeviz_workflow import PipeVizWorkflow
from src.pipeline.simulate_pipeline import PipelineSimulator
from src.pipeline.utils import (
    extract_function_assembly,
    read_json_data,
    write_json_data,
)

router = APIRouter(tags=["Pipeline Routes"], prefix="/api")


@router.get("/health", response_model=None)
async def do_health_check():
    try:
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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


@router.get("/get_mock_code")
async def get_mock_code(language: SupportedProgrammingLanguagesEnum):
    try:
        paths = WorkflowPaths()
        if language == SupportedProgrammingLanguagesEnum.C:
            code_path = paths.c_mock_path
        else:
            code_path = paths.cpp_mock_path

        with code_path.open("r") as f:
            code = f.readlines()
        return {"code": code}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/get_pipeline_details")
async def get_pipeline_details(pipeline_type: PipelineTypes):
    try:
        if pipeline_type == PipelineTypes.STATIC_IN_ORDER:
            stages = StaticInOrderStages
        elif pipeline_type == PipelineTypes.SCOREBOARD:
            stages = ScoreboardStages
        elif pipeline_type == PipelineTypes.DYNAMIC_IN_ORDER:
            stages = DynamicInOrderStages
        elif pipeline_type == PipelineTypes.IN_ORDER_SUPERSCALAR:
            stages = InOrderSuperscalarStages
        elif pipeline_type == PipelineTypes.VLIW:
            stages = VLIWStages
        elif pipeline_type == PipelineTypes.TOMASULO:
            stages = TomasuloStages
        elif pipeline_type == PipelineTypes.OUT_OF_ORDER:
            stages = OutOfOrderStages
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pipeline type"
            )

        return {
            "stages": [stages(stage).name for stage in stages.get_all_stages()],
            "structural_hazard_prone_stages": [
                stages(stage).name
                for stage in stages.get_structural_hazard_prone_stages()
            ],
            "raw_hazard_prone_stages": [
                stages(stage).name for stage in stages.get_raw_hazard_prone_stages()
            ],
            "war_hazard_prone_stages": [
                stages(stage).name for stage in stages.get_war_hazard_prone_stages()
            ],
            "waw_hazard_prone_stages": [
                stages(stage).name for stage in stages.get_waw_hazard_prone_stages()
            ],
            "final_stage": stages(stages.get_final_stage()).name,
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulate_pipelines", response_model=None)
async def simulate_pipelines(
    language: SupportedProgrammingLanguagesEnum,
    uuid: str | None = None,
    code: str = Body(default="", embed=True),
    mock_existing_code: bool = False,
    function_name: str = "main",
    pipeline_type: PipelineTypes = PipelineTypes.STATIC_IN_ORDER,
    compiler_optimization: CompilerOptimizationsEnum = CompilerOptimizationsEnum.LEVEL_0,
    enable_loop_unrolling: bool = False,
    enable_forwarding: bool = False,
):
    try:
        # set flag for a fresh treat everythign as new fresh run
        fresh_run = True
        # validate the code and generate assembly code
        if uuid is None:
            workflow_id = str(uuid4())
        else:
            workflow_id = uuid
            fresh_run = False
        workflow = PipeVizWorkflow(language, uuid=workflow_id)

        # clean the run directory for rerun of the workflow
        # so that everything will be clear and fresh for the new run
        if not fresh_run:
            workflow.clean()

        if mock_existing_code:
            if language == SupportedProgrammingLanguagesEnum.C:
                code_path = workflow._paths.c_mock_path
            elif language == SupportedProgrammingLanguagesEnum.CPP:
                code_path = workflow._paths.cpp_mock_path
            result, asm_path = workflow.generate_asembly_code(
                code_path, compiler_optimization, enable_loop_unrolling, False
            )
        else:
            # we are not running mock code, so we use the provided code
            if language == SupportedProgrammingLanguagesEnum.C:
                code_path = workflow.run_path / "test-fib.c"
            elif language == SupportedProgrammingLanguagesEnum.CPP:
                code_path = workflow.run_path / "test-fib.cpp"

            # lets write some pre checks to fail early
            if function_name not in code:  # dont lower since we expect the exact match
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="function_name not found in code",
                )

            with open(code_path, "w") as f:
                f.write(code)

            result, asm_path = workflow.generate_asembly_code(
                code_path, compiler_optimization, enable_loop_unrolling
            )

        if not result and not isinstance(asm_path, Path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate assembly code: {asm_path}",
            )

        # read the assembly code
        with asm_path.open("r") as f:
            asm_code = f.read()

        # Extract just the function (only real instruction lines)
        function_lines = extract_function_assembly(asm_code, function_name)

        if not function_lines:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Function '{function_name}' not found in assembly code.",
            )

        logger.info("Lets save the pipeline configuration for chat purposes..")
        chat_config_path: Path = workflow.get_chat_config_file()
        chat_history_path: Path = workflow.get_history_file()

        with code_path.open("r") as f:
            source_code = f.readlines()

        pipe_line_details = await get_pipeline_details(pipeline_type)

        chat_required_data = {
            "programming_language": language.value,
            "function_name": function_name,
            "compiler_flag": compiler_optimization.value,
            "loop_unrolling_factor": enable_loop_unrolling,
            "source_code": source_code,
            "assembly_code": function_lines,
            "pipeline_type": pipeline_type.value,
            "pipeline_stages": pipe_line_details.get("stages"),
            "previous_questions": [],
            "question": "",
        }

        write_json_data(chat_config_path, chat_required_data)

        logger.info("Analyzing Fibonacci function...")

        # Simulate with forwarding
        logger.info("SIMULATION WITH FORWARDING")
        logger.info("=" * 100)
        sim_forward = PipelineSimulator(
            pipeline_type=pipeline_type, enable_forwarding=enable_forwarding
        )
        sim_forward.load_instructions(function_lines)
        sim_forward.simulate()
        json_data = sim_forward.convert_to_json()

        markdown_data = sim_forward.convert_to_markdown(json_data)

        chat_required_data["generated_pipeline_simulation"] = markdown_data
        write_json_data(chat_config_path, chat_required_data)

        # check if it exists else create one
        if not chat_history_path.exists():
            chat_history_data = {"responses": []}
        else:
            chat_history_data = read_json_data(chat_history_path)
        write_json_data(chat_history_path, chat_history_data)

        # write the generated pipeline simulation to a new file
        write_json_data(
            workflow.get_pipeline_path(),
            {"pipeline_data": json_data, "type": pipeline_type},
        )

        return {"workflow_id": workflow.workflow_id, "pipelines": json_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
