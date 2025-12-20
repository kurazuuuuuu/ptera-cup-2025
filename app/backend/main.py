from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from src.auth import auth_backend, fastapi_users
from src.db import create_db_and_tables
from src.schemas import UserCreate, UserRead, UserUpdate
from src.time_line import router as timeline_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_db_and_tables()
    yield
    # Shutdown


app = FastAPI(lifespan=lifespan)

# /auth/jwt/login
# /auth/jwt/logout
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# /auth/register
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# /users
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# /posts (Timeline)
app.include_router(timeline_router)


@app.get("/")
async def root():
    return {"message": "Hello from backend!"}


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
