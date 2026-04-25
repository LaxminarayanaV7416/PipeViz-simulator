import base64
import json

from loguru import logger
from openai import OpenAI

from src.models.processor_config_models import ProcessorConfig

client = OpenAI()  # reads OPENAI_API_KEY from environment

_SYSTEM_PROMPT = (
    "You are a computer architecture expert. "
    "Extract every processor pipeline configuration parameter precisely from the given input. "
    "Do not infer or assume values that are not explicitly stated."
)

# Manually defined flat schema — avoids Pydantic's $defs/$ref which GPT-4o drops silently
_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_processor_config",
        "description": "Extract all processor pipeline configuration parameters from the description.",
        "parameters": {
            "type": "object",
            "properties": {
                "stages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Pipeline stage names in order, e.g. ['IF', 'IS', 'EX', 'WB', 'CO']",
                },
                "fetch_width": {
                    "type": "integer",
                    "description": "Max instructions fetched (IF stage) per cycle",
                },
                "issue_width": {
                    "type": "integer",
                    "description": "Max instructions issued (IS stage) per cycle",
                },
                "scheduling_policy": {
                    "type": "string",
                    "description": "'in_order', 'tomasulo', or 'out_of_order'",
                },
                "speculative_execution": {
                    "type": "boolean",
                    "description": "Whether speculative execution is enabled",
                },
                "execution_latencies": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                    "description": (
                        "Cycles each instruction type spends in EX stage. "
                        "Use 'default' key for all others not listed. "
                        "e.g. {'LD': 2, 'SD': 2, 'ADD.D': 2, 'MUL.D': 4, 'default': 1}"
                    ),
                },
                "forwarding_ready_stage": {
                    "type": "string",
                    "description": "Stage at the END of which dest register values are ready for forwarding, e.g. 'WB'",
                },
                "branch_prediction": {
                    "type": "string",
                    "description": "Branch prediction strategy: 'static_not_taken', 'static_always_taken', 'dynamic_bpb_btb', etc.",
                },
                "branch_resolution_stage": {
                    "type": "string",
                    "description": "Stage at the END of which branch outcome is resolved, e.g. 'WB'",
                },
                "commit_policy": {
                    "type": "string",
                    "description": "'in_order' — cannot commit out of order; 'out_of_order' — can commit out of order",
                },
                "multi_commit_allowed": {
                    "type": "boolean",
                    "description": "Whether multiple instructions can commit (WB/CO) in the same cycle",
                },
                "structural_hazards": {
                    "type": "boolean",
                    "description": "True if structural hazards exist; False if no structural hazards (unlimited reservation stations, functional units, etc.)",
                },
                "special_register_rules": {
                    "type": "array",
                    "description": "Special register readiness rules for specific instructions, e.g. SD base ready at EX, rt ready at CO",
                    "items": {
                        "type": "object",
                        "properties": {
                            "instruction_type": {
                                "type": "string",
                                "description": "e.g. 'SD'",
                            },
                            "register_name": {
                                "type": "string",
                                "description": "e.g. 'base' or 'rt'",
                            },
                            "ready_at_stage": {
                                "type": "string",
                                "description": "Stage at which this register must be ready, e.g. 'EX' or 'CO'",
                            },
                        },
                        "required": ["instruction_type", "register_name", "ready_at_stage"],
                    },
                },
            },
            "required": [
                "stages",
                "fetch_width",
                "issue_width",
                "scheduling_policy",
                "speculative_execution",
                "execution_latencies",
                "forwarding_ready_stage",
                "branch_prediction",
                "branch_resolution_stage",
                "commit_policy",
                "multi_commit_allowed",
                "structural_hazards",
                "special_register_rules",
            ],
        },
    },
}

_TOOL_CHOICE = {"type": "function", "function": {"name": "extract_processor_config"}}


def _parse_response(response) -> ProcessorConfig:
    tool_call = response.choices[0].message.tool_calls[0]
    data = json.loads(tool_call.function.arguments)
    return ProcessorConfig(**data)


def extract_from_text(text: str) -> ProcessorConfig:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Extract all processor pipeline configuration from this description:\n\n{text}",
            },
        ],
        tools=[_TOOL],
        tool_choice=_TOOL_CHOICE,
    )
    return _parse_response(response)


def extract_from_image(image_bytes: bytes, media_type: str) -> ProcessorConfig:
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{media_type};base64,{image_data}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {
                        "type": "text",
                        "text": (
                            "Extract all processor pipeline configuration from this image. "
                            "Pay close attention to execution latency cycles — look for phrases like "
                            "'X instructions need N clock cycles to complete the EX stage' and fill "
                            "execution_latencies with those values. Include a 'default' key for any "
                            "instruction types not explicitly mentioned."
                        ),
                    },
                ],
            },
        ],
        tools=[_TOOL],
        tool_choice=_TOOL_CHOICE,
    )
    return _parse_response(response)


def log_config(config: ProcessorConfig) -> None:
    logger.info("=" * 60)
    logger.info("EXTRACTED PROCESSOR CONFIG")
    logger.info("=" * 60)
    for field, value in config.model_dump().items():
        logger.info(f"  {field}: {value}")
    logger.info("=" * 60)
