import random

from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from coffee_shop.db.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Represents a user entity."""

    @staticmethod
    def generate_code() -> int:
        """Generate 6-digit code."""
        return random.randint(100000, 999999)
