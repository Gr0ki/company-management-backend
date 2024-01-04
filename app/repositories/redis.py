from json import loads, dumps
from redis.asyncio import Redis

from ..utils.app_loggers import get_logger
from ..core.settings import get_settings
from .base import AbstractRepository
from ..models.users import User


settings = get_settings()
logger = get_logger(__name__)


class RedisRepository(AbstractRepository):
    schema = None
    model_name = None

    @staticmethod
    def _convert_to_json_dict(data: dict, schema) -> str:
        result = loads(schema(**data).model_dump_json())
        result["hashed_password"] = data["hashed_password"]
        return dumps(result)

    @staticmethod
    def _convert_cached_data_to_dict(cashed_data: bytes) -> dict:
        return loads(cashed_data.decode())

    async def _get_redis_key_pattern_for_user(
        self, redis_session: Redis, id: int | None, email: str | None = None
    ) -> str | None:
        id = id or "*"
        email = email or "*"
        redis_key_pattern = await redis_session.scan(
            match=f"{self.model_name}:{id}:{email}"
        )
        if len(redis_key_pattern[1]) > 0:
            return redis_key_pattern[1][0]

    async def _get_redis_key_pattern(
        self,
        redis_session: Redis,
        id: int | None,
        email: str | None = None,
        is_adding: bool = False,
    ):
        if self.model_name == User.__tablename__:
            if is_adding is True:
                return f"{self.model_name}:{id}:{email}"
            else:
                return await self._get_redis_key_pattern_for_user(
                    redis_session, id, email
                )
        return f"{self.model_name}:{id}"

    async def find_one(
        self,
        redis_session: Redis,
        id: int | None,
        email: str | None = None,
    ) -> dict | None:
        key_pattern = await self._get_redis_key_pattern(redis_session, id, email)
        if key_pattern is not None:
            data = await redis_session.get(key_pattern)
            if data is not None:
                data = self._convert_cached_data_to_dict(data)
                logger.info(f"{self.model_name}'s data was taken from Redis.")
                return data

    async def add_one(
        self,
        data: dict | tuple | None,
        redis_session: Redis,
    ) -> None:
        if data is None or isinstance(data, tuple):
            return
        await redis_session.set(
            await self._get_redis_key_pattern(
                redis_session, data["id"], data["email"], is_adding=True
            ),
            self._convert_to_json_dict(data, self.schema),
            ex=settings.REDIS_EXPIRATION_TIME,
        )
        logger.info(f"{self.model_name}'s data was inserted in Redis.")

    async def delete_one(
        self, data: dict | tuple | None, id: int, redis_session: Redis
    ) -> None:
        key_pattern = await self._get_redis_key_pattern(redis_session, id)
        if key_pattern is not None:
            if isinstance(data, int):
                await redis_session.delete(key_pattern)
                logger.info(f"{self.model_name}'s data was deleted from Redis.")

    async def update_one(self):
        """Implementation isn't required."""
        pass

    async def find_all(self):
        """Implementation isn't required."""
        pass
