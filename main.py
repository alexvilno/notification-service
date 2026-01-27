from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.notifications import notifications_router
from core.config import setup_logging, app_config
from core.db import engine
from models.notifications import BaseModel

logger = setup_logging()


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
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
