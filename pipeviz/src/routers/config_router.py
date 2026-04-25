from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from loguru import logger

from src.models.processor_config_models import ProcessorConfig
from src.services.llm_extractor import extract_from_image, extract_from_text, log_config

router = APIRouter(tags=["Config Routes"], prefix="/api")

SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


@router.post("/extract_config", response_model=ProcessorConfig)
async def extract_config(
    text: str = Form(None),
    file: UploadFile = File(None),
):
    """
    Extract processor pipeline configuration from a text description or an image.
    Provide either `text` or `file` (image), not both.
    """
    if not text and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either a text description or an image file.",
        )

    if text and file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either text or an image file, not both.",
        )

    try:
        if file:
            media_type = file.content_type or "image/png"
            if media_type not in SUPPORTED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported image type '{media_type}'. Supported: {SUPPORTED_IMAGE_TYPES}",
                )
            logger.info(f"Extracting config from image: {file.filename} ({media_type})")
            image_bytes = await file.read()
            config = extract_from_image(image_bytes, media_type)
        else:
            logger.info("Extracting config from text input")
            config = extract_from_text(text)

        log_config(config)
        return config

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
