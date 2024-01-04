"""Contains fixtures for pytest tests."""

import asyncio
from datetime import timedelta
import pytest_asyncio
import faker
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy import insert, delete
from sqlalchemy.sql.expression import literal_column

from app.main import app
from app.models.users import User
from app.db.psql_config import async_session_maker
from app.utils.password_hashing import hash_password
from app.core.settings import get_settings
from app.services.jwt_handler import create_access_token


fake = faker.Faker()
settings = get_settings()


@pytest_asyncio.fixture(scope="session")
async def ac_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app, base_url=f"http://{settings.APP_HOST}:{settings.APP_PORT}"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
def get_random_user_data():
    def _random_user_data(
        email: str = fake.unique.email(),
        phone: str = fake.unique.phone_number()[:12],
        password: str = fake.unique.password(),
        firstname: str = fake.unique.first_name(),
        lastname: str = fake.unique.last_name(),
        city: str = fake.unique.city(),
        is_active: bool = fake.boolean(),
        is_superuser: bool = fake.boolean(),
        links: list = [fake.url(), fake.url()],
        avatar: str = fake.url(),
    ):
        return {
            "email": email,
            "phone": phone,
            "password": password,
            "firstname": firstname,
            "lastname": lastname,
            "city": city,
            "is_active": is_active,
            "is_superuser": is_superuser,
            "links": links,
            "avatar": avatar,
        }

    return _random_user_data


@pytest_asyncio.fixture(scope="session")
def new_user():
    async def _new_user(data: dict, user_model: type[User] = User):
        data["hashed_password"] = hash_password(data["password"])
        del data["password"]
        if len(data["phone"]) > 13:
            data["phone"] = data["phone"][:12]
        stmt = insert(user_model).values(**data).returning(literal_column("*"))
        async with async_session_maker() as session:
            new_user = await session.execute(stmt)
            await session.commit()
            new_user = dict(new_user.mappings().first().items())
            return new_user

    return _new_user


@pytest_asyncio.fixture(scope="session")
def delete_user():
    async def _delete_user(id: int, user_model: type[User] = User) -> bool:
        async with async_session_maker() as session:
            await session.execute(delete(user_model).where(user_model.id == id))
            await session.commit()

    return _delete_user


@pytest_asyncio.fixture(scope="session")
def create_jwt_localy():
    async def _create_jwt_localy(email: str, epires_delta: int | None = None):
        return create_access_token(
            email, epires_delta=timedelta(seconds=epires_delta or 1)
        )

    return _create_jwt_localy
