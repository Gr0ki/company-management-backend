"""Contains templates for error handling."""

from fastapi.exceptions import HTTPException

from ..utils.password_hashing import verify_password


def exception_message_template(key: str, message: str) -> list:
    return [
        {
            "type": "value_error",
            "loc": [key],
            "msg": message,
        },
    ]


def filter_error_handler_template(
    response, error: HTTPException, is_delete: bool = False
):
    if response is None:
        raise error
    elif is_delete is False:
        return response


def filter_response_for_404_error(response, model_name: str, is_delete: bool = False):
    return filter_error_handler_template(
        response,
        HTTPException(
            status_code=404,
            detail=exception_message_template("id", f"{model_name} not found!"),
        ),
        is_delete,
    )


def filter_response_for_409_error(response, model_name: str):
    response = filter_response_for_404_error(response, model_name)
    if isinstance(response, tuple):
        raise HTTPException(
            status_code=409, detail=exception_message_template(*response)
        )
    else:
        return response


def filter_response_for_401_error(response, model_name: str, is_delete: bool = False):
    return filter_error_handler_template(
        response,
        HTTPException(
            status_code=401,
            detail=exception_message_template(
                "id", f"Access denied, unknown {model_name}!"
            ),
        ),
        is_delete,
    )


def unauthorized_wrong_credentials():
    return HTTPException(
        status_code=401,
        detail=exception_message_template(
            "password", "Incorrect username or password!"
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )


def permition_restriction_error(message: str):
    return HTTPException(
        status_code=401,
        detail=exception_message_template("id", message),
        headers={"WWW-Authenticate": "Bearer"},
    )


def authentication_check(db_data, form_data, model_name) -> dict:
    filter_response_for_404_error(db_data, model_name)
    if not verify_password(form_data["password"], db_data["hashed_password"]):
        raise unauthorized_wrong_credentials()
    return db_data
