import json
from pathlib import Path

from src.enum_vault.workflow_enums import (
    SupportedProgrammingLanguagesEnum,
    WorkflowPaths,
)
from src.pipeline.utils import read_json_data


def read_asembly_code(workflow_id: str) -> str:
    asm_path = WorkflowPaths().get_asm_file(workflow_id)
    if not asm_path.exists():
        return ""
    with open(asm_path, "r") as f:
        return f.read()


def read_code(workflow_id: str) -> str:
    paths = WorkflowPaths()
    # read language from the config
    chat_config = read_json_data(paths.get_chat_config_file(workflow_id))
    language = chat_config.get("language", SupportedProgrammingLanguagesEnum.C)
    code_path = paths.get_code_file(workflow_id, language)
    if not code_path.exists():
        return ""
    with open(code_path, "r") as f:
        return f.read()


def read_pipeline(workflow_id: str) -> str:
    pipeline_path = WorkflowPaths().get_pipeline_path(workflow_id)
    if not pipeline_path.exists():
        return ""
    with pipeline_path.open("r") as f:
        return json.load(f)


def read_chat_history_from_file(workflow_id: str) -> list:
    paths = WorkflowPaths()
    chat_file_path: Path = paths.get_history_file(workflow_id)
    chat_config = read_json_data(chat_file_path)
    return chat_config.get("responses", [])


def get_compiler_flags(workflow_id: str) -> str:
    paths = WorkflowPaths()
    chat_config = read_json_data(paths.get_chat_config_file(workflow_id))
    flags_config = chat_config.get("compiler_flag", 0)
    return f"-O{flags_config}"


def get_loop_unrolling_flag(workflow_id: str) -> str:
    paths = WorkflowPaths()
    chat_config = read_json_data(paths.get_chat_config_file(workflow_id))
    flags_config = chat_config.get("loop_unrolling_factor", False)
    return flags_config


def get_openai_tools() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": "read_asembly_code",
                "description": "Read the generated AARCH64 assembly for a workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {"workflow_id": {"type": "string"}},
                    "required": ["workflow_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_code",
                "description": "Read the source code for a workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {"workflow_id": {"type": "string"}},
                    "required": ["workflow_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_pipeline",
                "description": "Read the pipeline simulation output for a workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {"workflow_id": {"type": "string"}},
                    "required": ["workflow_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_chat_history_from_file",
                "description": "Read prior question/response pairs for a workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {"workflow_id": {"type": "string"}},
                    "required": ["workflow_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_compiler_flags",
                "description": "Return the compiler optimization flag used for a workflow (e.g., -O2).",
                "parameters": {
                    "type": "object",
                    "properties": {"workflow_id": {"type": "string"}},
                    "required": ["workflow_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_loop_unrolling_flag",
                "description": "Return the loop unrolling flag or factor used for a workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {"workflow_id": {"type": "string"}},
                    "required": ["workflow_id"],
                },
            },
        },
    ]
