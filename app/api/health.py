"""Contains router for a base endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from ..db.redis_config import get_session as redis_session
from ..db.psql_config import get_async_session as psql_session
from ..utils.app_loggers import get_logger


logger = get_logger(module_name=__name__)

health_router = APIRouter(prefix="/health", tags=["health"])
response_ok = {"status_code": 200, "detail": "ok", "result": "working"}


@health_router.get("/redis")
async def health_check_redis(session: Redis = Depends(redis_session)):
    """Checks the health of the Redis connection."""

    try:
        await session.ping()
    except Exception as e:
        logger.error(f"Redis's health check: FAILURE! Operational error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis connection failed: {e}",
        )
    return response_ok


@health_router.get("/psql")
async def health_check_psql(session: AsyncSession = Depends(psql_session)):
    """Checks the health of the PostgreSQL connection."""

    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"PostgreSQL's health check: FAILURE! Operational error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"PostgreSQL connection failed: {e}",
        )
    return response_ok


@health_router.get("/app")
async def health_check():
    return response_ok
