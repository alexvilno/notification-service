import uvicorn
from fastapi import FastAPI

from api.notifications import notifications_router

app = FastAPI(title="Notification Service API")
app.include_router(notifications_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
