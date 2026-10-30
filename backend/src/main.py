from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routers.auth import router as auth_router
from src.api.routers.health import router as health_router
from src.api.routers.users import router as users_router
from src.core.config import settings
from src.core.database import engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(title="Nexora API", version="0.1.0", lifespan=lifespan)
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(users_router, prefix="/api/users")


@app.middleware("http")
async def enforce_same_origin_for_mutations(
    request: Request,
    call_next,
):
    if request.url.path.startswith("/api/") and request.method not in {
        "GET",
        "HEAD",
        "OPTIONS",
    }:
        if request.headers.get("origin") != settings.app_origin:
            return JSONResponse(
                status_code=403,
                content={"detail": "Request origin is not allowed"},
            )
    return await call_next(request)
