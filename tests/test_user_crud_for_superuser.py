"""
Contains tests for CRUD endpoints related to User model.
Requests from a superuser.
"""
import pytest
from httpx import Response
from json import loads, dumps

from app.schemas.users import UserSchema, SignUpRequestSchema, UserUpdateRequestSchema
from .conftest import fake


@pytest.mark.asyncio
async def test_retrive_user_list_as_superuser(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a User list as a superuser."""
    user = await new_user(get_random_user_data(is_superuser=True))
    user_jwt = await create_jwt_localy(user["email"])
    user = loads(UserSchema(**user).model_dump_json())
    response: Response = await ac_client.get(
        "/api/users/", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json()["users"], list)
    assert user in response.json()["users"]


# ______________________________________________________________________________


@pytest.mark.asyncio
async def test_retrive_user_as_superuser_detailed(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a User detailed as a superuser."""
    user = await new_user(get_random_user_data(is_superuser=True))
    user_jwt = await create_jwt_localy(user["email"])
    user = loads(UserSchema(**user).model_dump_json())
    response: Response = await ac_client.get(
        f"/api/users/{user['id']}", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 200
    assert user == response.json()


@pytest.mark.asyncio
async def test_retrive_user_as_superuser_detailed_miss(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a User detailed as a superuser. User miss (404)."""
    user = await new_user(get_random_user_data(is_superuser=True))
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.get(
        "/api/users/999", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "User not found!"


@pytest.mark.asyncio
async def test_retrive_user_detailed_as_superuser_unexpected_type(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests GET a User detailed as a superuser. Unexpected type for user id (422)."""
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
async def test_update_user_as_superuser(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT a User as a superuser."""
    user = await new_user(get_random_user_data(is_superuser=True))
    payload_dict = get_random_user_data()
    payload = UserUpdateRequestSchema(**payload_dict).model_dump_json()
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.put(
        url=f"/api/users/{user['id']}",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    del payload_dict["password"]
    assert response.status_code == 200
    for key, value in payload_dict.items():
        assert response.json()[key] == value


@pytest.mark.asyncio
async def test_update_another_user_as_superuser(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT another User as a superuser."""
    user_one = await new_user(get_random_user_data(is_superuser=True))
    user_two = await new_user(
        get_random_user_data(
            email=fake.unique.email(), phone=fake.unique.phone_number()[:12]
        )
    )
    user_dict = get_random_user_data(
        email=fake.unique.email(), phone=fake.unique.phone_number()[:12]
    )
    payload = UserUpdateRequestSchema(**user_dict).model_dump_json()
    user_jwt = await create_jwt_localy(user_one["email"])
    response: Response = await ac_client.put(
        url=f"/api/users/{user_two['id']}",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    for key in ("password", "email"):
        del user_dict[key]

    assert response.status_code == 200
    for key, value in user_dict.items():
        assert response.json()[key] == value


@pytest.mark.asyncio
async def test_update_user_as_superuser_miss(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT a User as a superuser. User miss (404)."""
    user_one = await new_user(get_random_user_data(is_superuser=True))
    user_jwt = await create_jwt_localy(user_one["email"])
    payload = UserUpdateRequestSchema(**get_random_user_data()).model_dump_json()
    response: Response = await ac_client.put(
        url="/api/users/999",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "User not found!"


@pytest.mark.asyncio
async def test_update_user_as_superuser_conflict(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT a User as a superuser with a conflicting input data (409 error)."""
    payload = get_random_user_data(is_superuser=True)
    user_one = await new_user(payload)
    payload = get_random_user_data(
        email=fake.unique.email(), phone=fake.unique.phone_number()[:12]
    )
    user_two = await new_user(payload)
    payload["phone"] = user_one["phone"]
    del payload["hashed_password"]
    payload["password"] = fake.unique.password()
    payload = UserUpdateRequestSchema(**payload).model_dump_json()
    user_jwt = await create_jwt_localy(user_one["email"])
    response: Response = await ac_client.put(
        url=f"/api/users/{user_two['id']}",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.status_code == 409
    assert response.json()["detail"][0]["msg"] == "Violation of the unique constraint!"


@pytest.mark.asyncio
async def test_update_user_as_superuser_unproccesible(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests PUT a User as a superuser with a conflicting input data (422 error)."""
    user = await new_user(get_random_user_data())
    payload = dumps(
        {
            "password": [fake.password()],
            "phone": [fake.word()],
            "firstname": [fake.word()],
            "lastname": [fake.word()],
            "city": [fake.word()],
            "links": [fake.url()],
            "avatar": fake.word(),
            "is_active": fake.boolean(),
            "is_superuser": True,
        }
    )
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.put(
        url=f"/api/users/{user['id']}",
        data=payload,
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.status_code == 422
    for elem in response.json()["detail"]:
        assert elem["msg"] == "Input should be a valid string"


# ______________________________________________________________________________


@pytest.mark.asyncio
async def test_delete_user_as_superuser(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests DELETE a User as a superuser."""
    user = await new_user(get_random_user_data(is_superuser=True))
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.delete(
        url=f"/api/users/{user['id']}", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_another_user_as_superuser(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests DELETE another a User as a superuser."""
    user_one = await new_user(get_random_user_data(is_superuser=True))
    user_two = await new_user(
        get_random_user_data(
            is_superuser=True,
            email=fake.unique.email(),
            phone=fake.unique.phone_number()[:12],
        )
    )
    user_jwt = await create_jwt_localy(user_one["email"])
    response: Response = await ac_client.delete(
        url=f"/api/users/{user_two['id']}",
        headers={"Authorization": f"Bearer {user_jwt}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_as_superuser_miss(
    ac_client, new_user, get_random_user_data, create_jwt_localy
):
    """Tests DELETE a User as a superuser. User miss (404)."""
    user = await new_user(get_random_user_data(is_superuser=True))
    user_jwt = await create_jwt_localy(user["email"])
    response: Response = await ac_client.delete(
        url="/api/users/999", headers={"Authorization": f"Bearer {user_jwt}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "User not found!"
