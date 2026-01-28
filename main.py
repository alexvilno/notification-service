"""
Точка входа
"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.notifications import notifications_router
from core.config import logger, app_config
from core.db import engine
from models.notifications import BaseModel


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    logger.info("starting application")
    logger.info(app_config)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Notification Service API", lifespan=lifespan)
app.include_router(notifications_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=app_config.app_host, port=app_config.app_port)
