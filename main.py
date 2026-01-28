"""
Точка входа
"""
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from api.notifications import notifications_router
from core.config import app_config
from core.db import engine
from models.notifications import BaseModel

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    logger.info("starting application")
    logger.info(
        "Docs: http://%s:%s/docs",
        app_config.app_host,
        app_config.app_port
    )
    logger.debug("config: %s",app_config)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield
    logger.info("graceful shutdown")
    await engine.dispose()


app = FastAPI(title="Notification Service API", lifespan=lifespan)
app.include_router(notifications_router)

@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    """
    Middleware для логирования входящих запросов
    """
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    process_time_ms = process_time * 1000

    logger.info(
        f"{request.method} {request.url.path} "
        f"{response.status_code} "
        f"{process_time_ms:.1f}ms"
    )

    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_config.app_host,
        port=app_config.app_port,
        log_level=logging.WARNING,
        workers=4
    )
