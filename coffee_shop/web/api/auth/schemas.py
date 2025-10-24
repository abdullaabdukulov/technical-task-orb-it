import uuid

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Represents a read command for a user."""


class UserCreate(schemas.BaseUserCreate):
    """Represents a create command for a user."""


class UserUpdate(schemas.BaseUserUpdate):
    """Represents an update command for a user."""


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(Token):
    refresh_token: str


class RefreshResponse(Token):
    pass


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str
