import os
from functools import total_ordering
from pathlib import Path

from loguru import logger
from openai import OpenAI

from src.config import PROMPT_TEMPLATE_PATH
from src.enum_vault.workflow_enums import WorkflowPaths
from src.pipeline.utils import (
    read_json_data,
    render_template,
    write_json_data,
)
from src.services.llm_tools import get_openai_tools

PROMPT_LIMIT = 75000  # no of words / tokens

LITELLM_HOST = os.getenv("LITELLM_HOST", "localhost")

model_type = os.getenv("MODEL_TYPE", "local")
if model_type == "cloud":
    client = OpenAI()
    MODEL_NAME = "gpt-4o"
else:
    client = OpenAI(
        base_url=f"http://{LITELLM_HOST}:4000/v1",
        api_key="my-master-key",
    )
    MODEL_NAME = "local-llama3.2"
    # MODEL_NAME = "local-llama3.2-8k"


def check_prompt_length(prompt: str) -> bool:
    prompt = prompt.replace("\n", " ")
    prompt = prompt.strip()
    prompt_list: list[str] = prompt.split(" ")
    return len(prompt_list) < PROMPT_LIMIT


def generate_prompt(prompt_data: dict) -> str:
    prompt = render_template(PROMPT_TEMPLATE_PATH, prompt_data)
    if check_prompt_length(prompt):
        return prompt
    else:
        raise ValueError("Prompt exceeds the maximum length")


def model_predict(prompt: str, paths: WorkflowPaths, workflow_id: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        # tools=get_openai_tools(),
    )
    return resp.choices[0].message.content


def ask_llm(workflow_id: str, question: str) -> str:
    paths = WorkflowPaths()
    chat_file_path: Path = paths.get_chat_config_file(workflow_id)
    chat_history = paths.get_history_file(workflow_id)
    chat_config = read_json_data(chat_file_path)
    chat_history_data = read_json_data(chat_history)
    # take current quesiton and move to previous asked questions
    previous_questions = chat_config.get("previous_questions", [])
    temp_question = chat_config.get("question", "")
    if temp_question:
        previous_questions.append(temp_question)
    chat_config["previous_questions"] = previous_questions
    chat_config["question"] = question
    # read pipeline and ingest into the prmpt
    pipeline_path = paths.get_pipeline_path(workflow_id)
    pipeline_data = read_json_data(pipeline_path)
    chat_config["json_pipeline"] = pipeline_data
    prompt = generate_prompt(chat_config)
    logger.info(f"Generated prompt: {prompt}")
    llm_response = model_predict(prompt, paths, workflow_id)
    logger.info(llm_response)
    question_llm_response = chat_history_data.get("responses", [])
    question_llm_response.append({"question": question, "response": llm_response})
    chat_history_data["responses"] = question_llm_response
    write_json_data(chat_history, chat_history_data)
    write_json_data(chat_file_path, chat_config)
    return llm_response
