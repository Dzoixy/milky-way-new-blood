from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),   # รองรับ bcrypt hash
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )