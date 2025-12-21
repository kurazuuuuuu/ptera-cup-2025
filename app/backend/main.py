from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from src.auth import auth_backend, fastapi_users
from src.db import create_db_and_tables
from src.schemas import UserCreate, UserRead, UserUpdate
from src.timeline import router as timeline_router
from src.routers.events import router as events_router
from src.routers.profile import router as profile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_db_and_tables()
    yield
    # Shutdown


app = FastAPI(lifespan=lifespan)

# Ensure storage directory exists
os.makedirs("storage/icons", exist_ok=True)

# Static files for icons
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# /v1/auth
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/v1/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/v1/auth",
    tags=["auth"],
)

# /v1/users
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/v1/users",
    tags=["users"],
)

# /v1/events
app.include_router(
    events_router,
    prefix="/v1/events",
    tags=["events"],
)

# /v1/profile
app.include_router(
    profile_router,
    prefix="/v1/profile",
    tags=["profile"],
)

# /v1/timeline
app.include_router(timeline_router, prefix="/v1/timeline", tags=["timeline"])

@app.get("/")
async def root():
    return {"message": "Hello from VibeCalendar Backend!"}


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
