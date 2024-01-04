"""Contains SQLAlchemy repository for User model."""
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import User
from ..schemas.users import UserSchema
from .sqlalchemy import SQLAlchemyRepository
from .redis import RedisRepository


class UserSQLARepository(SQLAlchemyRepository):
    model = User
    model_name = User.__tablename__


class UserRedisRepository(RedisRepository):
    schema = UserSchema
    model_name = User.__tablename__
