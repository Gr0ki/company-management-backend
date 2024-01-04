"""Contains app related configuration code."""

from functools import cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext


class Settings(BaseSettings):
    """Contains app's configs."""

    model_config = SettingsConfigDict(env_file=".env")

    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    DEV: bool

    TZ: str

    APP_NAME: str
    APP_HOST: str
    APP_PORT: int
    CORS_ORIGINS: list[str]
    CORS_HEADERS: list[str]

    ALGORITHMS: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DOMAIN: str
    API_AUDIENCE: str
    ISSUER: str
    AUTH0_JWKS_LINK: str

    PSQL_DB: str
    PSQL_USER: str
    PSQL_PASSWORD: str
    PSQL_HOST: str
    PSQL_PORT: int

    PSQL_TEST_DB: str
    PSQL_TEST_PORT: int

    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def SECRET_KEY_PRIVATE(self):
        """For encoding JWT token."""
        with open("/.ssh/id_rsa", "rb") as file:
            return file.read()

    @property
    def SECRET_KEY_PUB(self):
        """For decoding JWT token."""
        with open("/.ssh/id_rsa.pub.jwk", "rb") as file:
            return file.read()

    @property
    def REDIS_EXPIRATION_TIME(self) -> int:
        if {self.DEV} is True:
            return 1
        else:
            return 60 * 30

    @property
    def get_psql_url(self) -> str:
        """Returns an url for dev or prod psql db based on DEV value in .env file."""
        url = f"postgresql+asyncpg://{self.PSQL_USER}:{self.PSQL_PASSWORD}@{self.PSQL_HOST}:"

        if {self.DEV} is True:
            return url + f"{self.PSQL_TEST_PORT}/{self.PSQL_TEST_DB}"
        else:
            return url + f"{self.PSQL_PORT}/{self.PSQL_DB}"


@cache
def get_settings():
    """Returns Settings object. Cache supported."""
    return Settings()
