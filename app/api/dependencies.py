"""Contains dependancies for api endpoints."""

from ..services.users import UserService
from ..repositories.users import UserSQLARepository, UserRedisRepository


def get_user_service() -> UserService:
    return UserService(UserSQLARepository, UserRedisRepository)
