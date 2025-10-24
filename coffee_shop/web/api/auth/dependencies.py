import uuid

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from coffee_shop.db.dependencies import get_db_session
from coffee_shop.db.models.users import User
from coffee_shop.settings import settings
from coffee_shop.web.api.auth.strategies import TokenTypeJWTStrategy


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.users_secret
    verification_token_secret = settings.users_secret


async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


def get_access_jwt_strategy():
    return TokenTypeJWTStrategy(
        secret=settings.users_secret,
        lifetime_seconds=settings.access_token_lifetime,
        token_type="access",
    )


def get_refresh_jwt_strategy():
    return TokenTypeJWTStrategy(
        secret=settings.users_secret,
        lifetime_seconds=settings.refresh_token_lifetime,
        token_type="refresh",
    )


bearer_transport = BearerTransport(tokenUrl="/auth/login")

access_backend = AuthenticationBackend(
    name="access",
    transport=bearer_transport,
    get_strategy=get_access_jwt_strategy,
)

cookie_transport = CookieTransport(
    cookie_name="refresh_token",
    cookie_max_age=settings.refresh_token_lifetime,
    cookie_secure=False,
    cookie_httponly=True,
    cookie_samesite="lax",
)

refresh_backend = AuthenticationBackend(
    name="refresh",
    transport=cookie_transport,
    get_strategy=get_refresh_jwt_strategy,
)

backends = [access_backend, refresh_backend]

api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, backends)


async def get_access_enabled_backends(request: Request):
    return [access_backend]


current_active_user = api_users.current_user(
    active=True,
    get_enabled_backends=get_access_enabled_backends,
)


async def get_refresh_enabled_backends(request: Request):
    return [refresh_backend]


current_refresh_user = api_users.current_user(
    active=True,
    get_enabled_backends=get_refresh_enabled_backends,
)
