from app.schemas.users import UserUpdateRequestSchema
from app.utils.error_handlers import permition_restriction_error


def check_ownership(current_user: dict, requested_id: int | None = None):
    if (not current_user["is_superuser"]) and (
        requested_id is None or current_user["id"] != requested_id
    ):
        raise permition_restriction_error("You have no access to this resource!")


def check_user_fields_permithon_on_update(
    current_user: dict, update_form: UserUpdateRequestSchema
):
    is_superuser = current_user["is_superuser"]
    update_form = update_form.model_dump()
    current_user["password"] = current_user["hashed_password"]
    current_user = UserUpdateRequestSchema.model_validate(current_user).model_dump()
    for key in ("password", "firstname", "lastname"):
        del current_user[key]
        del update_form[key]
    if not is_superuser and current_user != update_form:
        raise permition_restriction_error(
            "You are not allowed to change any User field except for your password, firstname and lastname!"
        )


def check_user_update_permitions(
    current_user: dict,
    update_form: UserUpdateRequestSchema,
    requested_id: int | None = None,
):
    check_ownership(current_user, requested_id)
    check_user_fields_permithon_on_update(current_user, update_form)
