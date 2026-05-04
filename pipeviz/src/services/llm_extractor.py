import os
from pathlib import Path

from loguru import logger
from openai import OpenAI

from src.config import PROMPT_TEMPLATE_PATH
from src.enum_vault.workflow_enums import WorkflowPaths
from src.pipeline.utils import (
    read_json_data,
    render_template,
    update_chat_required_data,
)

PROMPT_LIMIT = 75000  # no of words / tokens

LITELLM_HOST = os.getenv("LITELLM_HOST", "localhost")
MODEL_NAME = "local-llama3.2"

client = OpenAI(
    base_url=f"http://{LITELLM_HOST}:4000/v1",
    api_key="my-master-key",
)


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


def ask_llm(workflow_id: str, question: str) -> str:
    paths = WorkflowPaths()
    chat_file_path: Path = paths.get_chat_config_file(workflow_id)
    chat_config = read_json_data(chat_file_path)
    # take current quesiton and move to previous asked questions
    previous_questions = chat_config.get("previous_questions", [])
    temp_question = chat_config.get("question", "")
    if temp_question:
        previous_questions.append(temp_question)
    chat_config["previous_questions"] = previous_questions
    chat_config["question"] = question
    update_chat_required_data(chat_file_path, chat_config)
    prompt = generate_prompt(chat_config)
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=prompt,
    )
    llm_response = resp.choices[0].message.content
    logger.info(llm_response)
    return llm_response
