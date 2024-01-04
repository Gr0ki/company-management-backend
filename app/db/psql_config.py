"""Contains Postgresql-related configs and tools."""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from ..core.settings import get_settings


settings = get_settings()
async_engine = create_async_engine(
    url=settings.get_psql_url,
    echo=settings.DEV,
    future=True,
)
async_session_maker = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


class Base(DeclarativeBase):
    pass
