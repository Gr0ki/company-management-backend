"""Contains API router config."""

from fastapi import APIRouter

from .auth import auth_router
from .users import users_router
from .health import health_router


routers = (
    auth_router,
    users_router,
    health_router,
)

api_router = APIRouter(prefix="/api")
for router in routers:
    api_router.include_router(router)
