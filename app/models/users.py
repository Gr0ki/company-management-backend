"""Contains db models."""

from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Boolean, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from ..db.psql_config import Base


class User(Base):
    """Sqlachemy model."""

    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        String(255), unique=False, nullable=False
    )
    phone: Mapped[str] = mapped_column(String(13), unique=True, nullable=True)
    firstname: Mapped[str] = mapped_column(String(70), unique=False, nullable=False)
    lastname: Mapped[str] = mapped_column(String(70), unique=False, nullable=True)
    city: Mapped[str] = mapped_column(String(255), unique=False, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, unique=False, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, unique=False, nullable=False
    )
    links: Mapped[List[str]] = mapped_column(
        ARRAY(item_type=String(255)), unique=False, nullable=True
    )
    avatar: Mapped[str] = mapped_column(String(255), unique=False, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.utcnow, unique=False, nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        unique=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, email={self.email},"
            + f" status={self.is_active}, is_superuser={self.is_superuser}"
        )
