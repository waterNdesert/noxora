import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db_session

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", response_model=None)
async def readiness(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object] | JSONResponse:
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Readiness check failed: PostgreSQL is unavailable")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "dependencies": {"database": "unavailable"}},
        )
    return {"status": "ready", "dependencies": {"database": "available"}}


@router.get("/version")
async def version() -> dict[str, str]:
    return {"name": "Nexora API", "version": settings.app_version}
