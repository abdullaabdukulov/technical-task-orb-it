from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from coffee_shop.db.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Represents a user entity."""

