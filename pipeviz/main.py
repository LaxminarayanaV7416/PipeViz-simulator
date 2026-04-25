"""
Main module for the PipeViz simulator.
this will start the simulator backend.

Authors:
    - Laxminarayana Vadnala <lvadnala@nd.edu>
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.pipeline.utils import get_args
from src.routers import config_router, pipeline_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # startup
    logger.info("FastAPI application is starting up...")
    yield
    # shutdown
    logger.info("FastAPI application is shutting down...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline_router.router)
app.include_router(config_router.router)

if __name__ == "__main__":
    args = get_args()
    uvicorn.run("main:app", host="0.0.0.0", port=args.port, reload=args.reload)
