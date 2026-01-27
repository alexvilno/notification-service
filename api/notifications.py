from fastapi import APIRouter
from starlette import status

notifications_router = APIRouter(prefix="/api/notifications")


@notifications_router.post(path="/", status_code=status.HTTP_201_CREATED)
async def create_notification():
    pass


@notifications_router.get(path="/{user_id}", status_code=status.HTTP_200_OK)
async def get_notification(user_id: int):
    pass
