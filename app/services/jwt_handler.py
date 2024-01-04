from typing import Tuple
from functools import cache
from datetime import timedelta
from datetime import datetime
from httpx import Client
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError


from ..utils.error_handlers import (
    exception_message_template,
)
from ..core.settings import get_settings
from ..utils.app_loggers import get_logger


logger = get_logger(__name__)
settings = get_settings()


@cache
def get_auth0_key():
    with Client() as client:
        return client.get(url=settings.AUTH0_JWKS_LINK).json()


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme.lower() == "bearer":
                raise HTTPException(
                    status_code=403,
                    detail=exception_message_template(
                        "JWT", "Invalid authentication scheme."
                    ),
                )
            return credentials.credentials

        else:
            raise HTTPException(
                status_code=403,
                detail=exception_message_template("JWT", "Invalid authorization code."),
            )


def create_access_token(
    email: str,
    epires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:
    return jwt.encode(
        {
            "sub": email,
            "exp": datetime.utcnow() + epires_delta,
            "aud": settings.API_AUDIENCE,
            "iss": settings.ISSUER,
        },
        key=settings.SECRET_KEY_PRIVATE,
        algorithm=settings.ALGORITHMS,
    )


def decode_jwt(token: str, secret_key: str | dict) -> dict:
    claims = jwt.decode(
        token=token,
        key=secret_key,
        algorithms=settings.ALGORITHMS,
        audience=settings.API_AUDIENCE,
        issuer=settings.ISSUER,
    )
    return claims


def verify(token: str) -> dict | None:
    try:
        return decode_jwt(token, settings.SECRET_KEY_PUB)
    except JWTError as e:
        try:
            claims = decode_jwt(token, get_auth0_key())
            claims["sub"] = claims["email"]
            del claims["email"]
            return claims

        except:
            raise HTTPException(
                status_code=403,
                detail=exception_message_template(
                    "JWT",
                    str(e),
                ),
            )


def get_current_user_email(token: str) -> Tuple[str, str]:
    token = verify(token)
    if token is not None:
        provider = "localhost" if isinstance(token["aud"], str) else "auth0"
        return token["sub"], provider
