from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_user_service
from ..services.users import UserService
from ..schemas.users import (
    SignInRequestSchema,
    TokenSchema,
)
from ..db.redis_config import get_session
from ..db.psql_config import get_async_session as psql_session


auth_router = APIRouter(prefix="/auth", tags=["users"])


@auth_router.post("/login", response_model=TokenSchema, status_code=200)
async def login(
    login_form: SignInRequestSchema,
    users_service: Annotated[UserService, Depends(get_user_service)],
    redis_session: Redis = Depends(get_session),
    psql_session: AsyncSession = Depends(psql_session),
):
    return await users_service.login(
        redis_session,
        psql_session,
        login_form,
    )
