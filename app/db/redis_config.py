"""Contains Redis-related configs and tools."""

from redis.asyncio import Redis

from ..core.settings import get_settings


settings = get_settings()


async def get_session() -> Redis:
    async with Redis(
        password=settings.REDIS_PASSWORD,
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    ) as session:
        yield session
