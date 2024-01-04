"""Contains endpoints for Users model."""

from typing import Annotated
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.jwt_handler import JWTBearer

from .dependencies import get_user_service
from ..services.users import UserService
from ..models.users import User
from ..schemas.users import (
    SignUpRequestSchema,
    UserSchema,
    UsersListResponseSchema,
    UserUpdateRequestSchema,
)
from ..db.redis_config import get_session
from ..db.psql_config import get_async_session as psql_session
from ..utils.error_handlers import (
    filter_response_for_404_error,
    filter_response_for_409_error,
)
from ..services.user_permitions import check_ownership, check_user_update_permitions


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get(
    "/me", response_model=UserSchema, status_code=200, summary="Get current User"
)
async def get_current_user(
    token: Annotated[str, Depends(JWTBearer())],
    users_service: Annotated[UserService, Depends(get_user_service)],
    redis_session: Redis = Depends(get_session),
    psql_session: AsyncSession = Depends(psql_session),
):
    return await users_service.get_current_user(redis_session, psql_session, token)


@users_router.post("/", response_model=UserSchema, status_code=201)
async def create_user(
    create_form: SignUpRequestSchema,
    users_service: Annotated[UserService, Depends(get_user_service)],
    redis_session: Redis = Depends(get_session),
    psql_session: AsyncSession = Depends(psql_session),
):
    return filter_response_for_409_error(
        await users_service.add_user(create_form, redis_session, psql_session),
        User.__tablename__,
    )


@users_router.get("/{id}", response_model=UserSchema)
async def get_user(
    id: int,
    token: Annotated[str, Depends(JWTBearer())],
    users_service: Annotated[UserService, Depends(get_user_service)],
    redis_session: Redis = Depends(get_session),
    psql_session: AsyncSession = Depends(psql_session),
):
    current_user = await users_service.get_current_user(
        redis_session, psql_session, token
    )
    check_ownership(current_user, id)
    return filter_response_for_404_error(
        await users_service.get_user(redis_session, psql_session, id),
        User.__tablename__,
    )


@users_router.get("/", response_model=UsersListResponseSchema)
async def get_users(
    token: Annotated[str, Depends(JWTBearer())],
    users_service: Annotated[UserService, Depends(get_user_service)],
    redis_session: Redis = Depends(get_session),
    psql_session: AsyncSession = Depends(psql_session),
):
    current_user = await users_service.get_current_user(
        redis_session, psql_session, token
    )
    check_ownership(current_user)
    return await users_service.get_users(psql_session)


@users_router.delete("/{id}", status_code=204)
async def delete_user(
    id: int,
    token: Annotated[str, Depends(JWTBearer())],
    users_service: Annotated[UserService, Depends(get_user_service)],
    redis_session: Redis = Depends(get_session),
    psql_session: AsyncSession = Depends(psql_session),
):
    current_user = await users_service.get_current_user(
        redis_session, psql_session, token
    )
    check_ownership(current_user, id)
    return filter_response_for_404_error(
        await users_service.delete_user(id, redis_session, psql_session),
        User.__tablename__,
        is_delete=True,
    )


@users_router.put("/{id}", response_model=UserSchema)
async def update_user(
    id: int,
    token: Annotated[str, Depends(JWTBearer())],
    update_form: UserUpdateRequestSchema,
    users_service: Annotated[UserService, Depends(get_user_service)],
    redis_session: Redis = Depends(get_session),
    psql_session: AsyncSession = Depends(psql_session),
):
    current_user = await users_service.get_current_user(
        redis_session, psql_session, token
    )
    check_user_update_permitions(current_user, update_form, id)
    return filter_response_for_409_error(
        await users_service.update_user(id, update_form, redis_session, psql_session),
        User.__tablename__,
    )
