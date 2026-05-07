import os

import requests
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from src.services.llm_extractor import ask_llm
from src.services.llm_tools import read_chat_history_from_file

router = APIRouter(tags=["LLM Chat Routes"], prefix="/api")


@router.get("/llm_health")
async def health():
    try:
        model_type = os.getenv("MODEL_TYPE", "local")
        if model_type == "local":
            response = requests.get(
                "http://localhost:4000/v1/models",
                headers={"Authorization": "Bearer my-master-key"},
                data={},
            )
            logger.info(f"Health check: {response.status_code}")
            return {"status": "ok"}
        else:
            # cloud model health check
            return {"status": "ok"}
    except requests.RequestException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Health check failed"
        )


@router.post("/chat", response_model=None)
async def chat(
    workflow_id: str,
    question: str,
):
    """
    Extract processor pipeline configuration from a text description or an image.
    Provide either `text` or `file` (image), not both.
    """
    try:
        logger.info(f"Received question: {question}")
        response = ask_llm(workflow_id, question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/chat_history")
async def get_chat_history(
    workflow_id: str,
):
    try:
        logger.info(f"Fetching chat history for workflow_id: {workflow_id}")
        chat_history = read_chat_history_from_file(workflow_id)
        return {"chat_history": chat_history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
