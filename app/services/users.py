"""Contains user related services."""

from typing import Dict, List
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from ..schemas.users import (
    SignUpRequestSchema,
    UserUpdateRequestSchema,
)
from ..models.users import User
from ..repositories.sqlalchemy import AbstractRepository
from ..utils.password_hashing import hash_password
from ..utils.error_handlers import (
    authentication_check,
)
from .jwt_handler import (
    create_access_token,
    get_current_user_email,
)
from ..utils.error_handlers import filter_response_for_401_error


fake = Faker()


class UserService:
    def __init__(
        self, user_sqla_repo: AbstractRepository, user_redis_repo: AbstractRepository
    ):
        self.users_sqla_repo: AbstractRepository = user_sqla_repo()
        self.users_redis_repo: AbstractRepository = user_redis_repo()

    async def _login_and_authenticaticate(
        self, redis_session: Redis, psql_session: AsyncSession, login_data: dict
    ):
        return authentication_check(
            await self.get_user(redis_session, psql_session, None, login_data["email"]),
            login_data,
            User.__tablename__,
        )

    async def add_user(
        self,
        create_form: SignUpRequestSchema,
        redis_session: Redis,
        psql_session: AsyncSession,
    ) -> Dict | tuple[str, str]:
        user_dict = create_form.model_dump(by_alias=True)
        user_dict["hashed_password"] = hash_password(user_dict["hashed_password"])
        user = await self.users_sqla_repo.add_one(user_dict, psql_session)
        await self.users_redis_repo.add_one(user, redis_session)
        return user

    async def get_user(
        self,
        redis_session: Redis,
        psql_session: AsyncSession,
        user_id: int | None,
        email: str | None = None,
    ) -> Dict | None:
        """Attems Redis hit: on a miss, returns query from the db; on Redis hit returns the user from it."""
        user_from_redis = await self.users_redis_repo.find_one(
            redis_session, user_id, email
        )
        user = user_from_redis or await self.users_sqla_repo.find_one(
            psql_session, user_id, email
        )
        if user_from_redis is None:
            await self.users_redis_repo.add_one(user, redis_session)
        return user

    async def get_users(
        self, psql_session: AsyncSession
    ) -> Dict[str, List[User]] | Dict[str, List]:
        return {"users": await self.users_sqla_repo.find_all(psql_session)}

    async def delete_user(
        self,
        user_id: int,
        redis_session: Redis,
        psql_session: AsyncSession,
    ) -> int | None:
        result = await self.users_sqla_repo.delete_one(user_id, psql_session)
        await self.users_redis_repo.delete_one(result, user_id, redis_session)
        return result

    async def update_user(
        self,
        user_id: int,
        update_form: UserUpdateRequestSchema,
        redis_session: Redis,
        psql_session: AsyncSession,
    ) -> User | tuple | None:
        user_dict = update_form.model_dump(exclude_unset=True)
        user_dict["hashed_password"] = hash_password(user_dict["password"])
        del user_dict["password"]
        user = await self.users_sqla_repo.update_one(user_id, user_dict, psql_session)
        await self.users_redis_repo.add_one(user, redis_session)
        return user

    async def _on_auth0_provider_create_user(
        self,
        redis_session: Redis,
        psql_session: AsyncSession,
        email: str,
        provider: str,
    ):
        if provider == "auth0":
            return await self.add_user(
                SignUpRequestSchema(
                    email=email, password=fake.password(), firstname="", lastname=""
                ),
                redis_session,
                psql_session,
            )

    async def login(
        self,
        redis_session: Redis,
        psql_session: AsyncSession,
        login_data,
    ) -> Dict | None:
        return {
            "access_token": create_access_token(
                (
                    await self._login_and_authenticaticate(
                        redis_session,
                        psql_session,
                        login_data.model_dump(),
                    )
                )["email"]
            ),
            "token_type": "bearer",
        }

    async def get_current_user(
        self,
        redis_session: Redis,
        psql_session: AsyncSession,
        token: str,
    ) -> Dict:
        email, provider = get_current_user_email(token)
        return filter_response_for_401_error(
            await self.get_user(redis_session, psql_session, None, email)
            or await self._on_auth0_provider_create_user(
                redis_session, psql_session, email, provider
            ),
            User.__tablename__,
        )
