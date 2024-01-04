"""
Contains tests for CRUD endpoints related to User model.
Requests from regular user.
"""
import pytest
from httpx import Response
from json import loads, dumps

from app.schemas.users import UserSchema, SignUpRequestSchema, UserUpdateRequestSchema
from .conftest import fake


@pytest.mark.asyncio
async def test_retrive_user_list_as_regular_user(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a User list as a regular user."""
    user = await new_user(get_random_user_data(is_superuser=False))
    user_jwt = await create_jwt_localy(user["email"])
    user = loads(UserSchema(**user).model_dump_json())
    response: Response = await ac_client.get(
        "/api/users/", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"][0]["msg"] == "You have no access to this resource!"


# ______________________________________________________________________________


@pytest.mark.asyncio
async def test_retrive_user_as_regular_user_detailed(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a User detailed as a regular user."""
    user = await new_user(get_random_user_data(is_superuser=False))
    user_jwt = await create_jwt_localy(user["email"])
    user = loads(UserSchema(**user).model_dump_json())
    response: Response = await ac_client.get(
        f"/api/users/{user['id']}", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 200
    assert user == response.json()


@pytest.mark.asyncio
async def test_retrive_user_as_regular_user_detailed_miss(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a User detailed as a regular user. Access denied (401)."""
    user = await new_user(get_random_user_data(is_superuser=False))
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.get(
        "/api/users/999", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"][0]["msg"] == "You have no access to this resource!"


@pytest.mark.asyncio
async def test_retrive_user_detailed_as_regular_user_unexpected_type(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a User detailed as a regular user. Unexpected type for user id (422)."""
    user = await new_user(get_random_user_data(is_superuser=True))
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.get(
        "/api/users/sdfg", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )


# ______________________________________________________________________________


@pytest.mark.asyncio
async def test_create_user(ac_client, get_random_user_data):
    """Tests POST a new User as a regular user."""
    user_signup_data = SignUpRequestSchema(**get_random_user_data()).model_dump_json()
    response: Response = await ac_client.post(url="/api/users/", data=user_signup_data)
    user_signup_data = loads(user_signup_data)
    del user_signup_data["password"]
    assert response.status_code == 201
    for key, value in user_signup_data.items():
        assert response.json()[key] == value


@pytest.mark.asyncio
async def test_create_user_conflict(ac_client, new_user, get_random_user_data):
    """Tests POST a new User as a regular user with a conflicting input data (409 error)."""
    user = await new_user(get_random_user_data())
    user["password"] = fake.unique.password()
    user = SignUpRequestSchema(**user).model_dump_json()
    response: Response = await ac_client.post(url="/api/users/", data=user)
    assert response.status_code == 409
    assert response.json()["detail"][0]["loc"][0] == "email"
    assert response.json()["detail"][0]["msg"] == "Violation of the unique constraint!"


@pytest.mark.asyncio
async def test_create_user_unproccesible(ac_client):
    """Tests POST a new User with a conflicting input data as a regular user (422 error)."""
    payload = dumps({"email": [], "password": {}, "firstname": 1223, "lastname": 467})
    response: Response = await ac_client.post(url=f"/api/users/", data=payload)
    assert response.status_code == 422
    for elem in response.json()["detail"]:
        assert elem["msg"] == "Input should be a valid string"


# ______________________________________________________________________________


@pytest.mark.asyncio
async def test_update_user_as_regular_user(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT a User as a regular user."""
    payload_dict = get_random_user_data(is_superuser=False)
    user = await new_user(payload_dict)
    payload_dict["password"] = fake.unique.password()
    payload_dict["firstname"] = fake.unique.first_name()
    payload_dict["lastname"] = fake.unique.last_name()
    payload = UserUpdateRequestSchema(**payload_dict).model_dump_json()

    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.put(
        url=f"/api/users/{user['id']}",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    for key in ("hashed_password", "password", "email"):
        del payload_dict[key]

    assert response.status_code == 200
    for key, value in payload_dict.items():
        assert response.json()[key] == value


@pytest.mark.asyncio
async def test_update_restricted_fields_for_user_as_regular_user(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT a User as a regular user."""
    payload_dict = get_random_user_data(is_superuser=False)
    user = await new_user(payload_dict)
    payload_dict["city"] = fake.unique.word()
    del payload_dict["hashed_password"]
    payload_dict["password"] = fake.unique.password()
    payload = UserUpdateRequestSchema(**payload_dict).model_dump_json()
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.put(
        url=f"/api/users/{user['id']}",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.status_code == 401
    assert (
        response.json()["detail"][0]["msg"]
        == "You are not allowed to change any User field except for your password, firstname and lastname!"
    )


@pytest.mark.asyncio
async def test_update_another_user_as_regular_user(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT another a User as a regular user."""
    user_one = await new_user(get_random_user_data(is_superuser=False))
    user_two = await new_user(
        get_random_user_data(
            email=fake.unique.email(),
            phone=fake.unique.phone_number()[:12],
            is_superuser=False,
        )
    )
    payload = UserUpdateRequestSchema(**get_random_user_data()).model_dump_json()
    user_jwt = await create_jwt_localy(user_one["email"])
    response: Response = await ac_client.put(
        url=f"/api/users/{user_two['id']}",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"][0]["msg"] == "You have no access to this resource!"


@pytest.mark.asyncio
async def test_update_user_as_regular_user_miss(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT a User as a regular user. User miss (401)."""
    user = await new_user(get_random_user_data(is_superuser=False))
    user_jwt = await create_jwt_localy(user["email"])
    payload = UserUpdateRequestSchema(**get_random_user_data()).model_dump_json()
    response: Response = await ac_client.put(
        url="/api/users/999",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"][0]["msg"] == "You have no access to this resource!"


# ______________________________________________________________________________


@pytest.mark.asyncio
async def test_delete_user_as_regular_user(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests DELETE a User as a regular user."""
    user = await new_user(get_random_user_data(is_superuser=False))
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.delete(
        url=f"/api/users/{user['id']}", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_another_user_as_regular_user(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests DELETE another a User as a regular user. Access denied (401)."""
    user_one = await new_user(get_random_user_data(is_superuser=False))
    user_two = await new_user(
        get_random_user_data(
            is_superuser=False,
            email=fake.unique.email(),
            phone=fake.unique.phone_number()[:12],
        )
    )
    user_jwt = await create_jwt_localy(user_one["email"])
    response: Response = await ac_client.delete(
        url=f"/api/users/{user_two['id']}",
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"][0]["msg"] == "You have no access to this resource!"


@pytest.mark.asyncio
async def test_delete_user_as_regular_user_miss(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests DELETE a User as a regular user. Access denied (401)."""
    user = await new_user(get_random_user_data(is_superuser=False))
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.delete(
        url="/api/users/999", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"][0]["msg"] == "You have no access to this resource!"
