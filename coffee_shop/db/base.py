from sqlalchemy.orm import DeclarativeBase

from coffee_shop.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
