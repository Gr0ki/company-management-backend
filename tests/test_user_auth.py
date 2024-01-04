"""Contains tests for user auth related endpoints."""
import asyncio
import re
import pytest
from httpx import Response
from json import loads, dumps

from .conftest import fake
from app.schemas.users import UserSchema


@pytest.mark.asyncio
async def test_login_existing_user(ac_client, new_user, get_random_user_data):
    """Tests login an existing user: POST -> 200 (jwt in response)"""
    user_data = get_random_user_data()
    password = user_data["password"]
    user = await new_user(user_data)
    response: Response = await ac_client.post(
        url="/api/auth/login",
        data=dumps({"email": user["email"], "password": password}),
    )
    assert response.status_code == 200
    assert isinstance(response.json()["access_token"], str)
    assert response.json()["token_type"].lower() == "bearer"


@pytest.mark.asyncio
async def test_login_unknown_user(ac_client):
    """Tests login an with unknown user data: POST -> 404"""
    response: Response = await ac_client.post(
        url="/api/auth/login",
        data=dumps({"email": fake.unique.email(), "password": fake.unique.password()}),
    )
    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "User not found!"


@pytest.mark.asyncio
async def test_login_existing_user_with_wrong_password(
    ac_client, new_user, get_random_user_data
):
    """Tests login an with wrong user password on matched user email: POST -> 401"""
    response: Response = await ac_client.post(
        url="/api/auth/login",
        data=dumps(
            {
                "email": (await new_user(get_random_user_data()))["email"],
                "password": fake.unique.password(),
            }
        ),
    )
    assert response.status_code == 401
    assert response.json()["detail"][0]["msg"] == "Incorrect username or password!"


@pytest.mark.asyncio
async def test_login_with_invalid_user_email(ac_client):
    """Tests login an invalid user email form: POST -> 422"""
    response: Response = await ac_client.post(
        url="/api/auth/login",
        data=dumps(
            {
                "email": fake.word(),
                "password": fake.unique.password(),
            }
        ),
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][1] == "email"
    assert re.match(
        r"value is not a valid email address:*", response.json()["detail"][0]["msg"]
    )


# ______________________________________________________________________________


@pytest.mark.asyncio
async def test_retrive_current_user_with_local_jwt(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a current User with JWT provided by app's server: GET -> 200"""
    user = loads(
        UserSchema(**(await new_user(get_random_user_data()))).model_dump_json()
    )
    response: Response = await ac_client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {(await create_jwt_localy(user['email']))}"},
    )
    assert response.status_code == 200
    assert response.json() == user


@pytest.mark.asyncio
async def test_retrive_current_user_with_expired_jwt(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a current User with expired JWT: GET -> 403"""
    user_jwt = await create_jwt_localy(
        (await new_user(get_random_user_data()))["email"], epires_delta=1
    )
    await asyncio.sleep(1.8)
    response: Response = await ac_client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {user_jwt}"}
    )  # flaky
    assert response.status_code == 403
    assert response.json()["detail"][0]["loc"][0] == "JWT"
    assert response.json()["detail"][0]["msg"] == "Signature has expired."


@pytest.mark.asyncio
async def test_retrive_current_user_with_valid_jwt_but_with_prior_user_deletiton(
    ac_client, new_user, get_random_user_data, delete_user, create_jwt_localy
):
    """Tests GET a current User with valid JWT, but user were deleted: GET -> 401"""
    user = await new_user(get_random_user_data())
    user_jwt = await create_jwt_localy(user["email"], epires_delta=1)
    await delete_user(user["id"])
    response: Response = await ac_client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"][0]["loc"][0] == "id"
    assert response.json()["detail"][0]["msg"] == "Access denied, unknown User!"


@pytest.mark.asyncio
async def test_retrive_current_user_with_invalid_jwt(
    ac_client,
):
    """Tests GET a current User with invalid JWT: GET -> 403"""
    response: Response = await ac_client.get(
        "/api/users/me", headers={"Authorization": fake.word()}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_retrive_current_user_with_absence_of_credentials_scheme_name(
    ac_client,
):
    """Tests GET a current User with absence of credentials scheme name: GET -> 403"""
    response: Response = await ac_client.get("/api/users/me")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_retrive_current_user_with_invalid_credentials_scheme_name(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a current User with invalid credentials scheme name: GET -> 403"""
    user_jwt = await create_jwt_localy(
        (await new_user(get_random_user_data()))["email"], epires_delta=1
    )
    response: Response = await ac_client.get(
        "/api/users/me", headers={"Authorization": f"{fake.word()} {user_jwt}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid authentication credentials"
