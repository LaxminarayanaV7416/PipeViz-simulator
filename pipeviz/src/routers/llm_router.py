from fastapi import APIRouter, HTTPException, status
from loguru import logger

from src.services.llm_extractor import ask_llm

router = APIRouter(tags=["LLM Chat Routes"], prefix="/api")


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
