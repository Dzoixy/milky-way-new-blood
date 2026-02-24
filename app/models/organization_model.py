from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True   # 🔥 กันชื่อซ้ำ (สำคัญใน SaaS)
    )

    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete"
    )

    patients = relationship(
        "Patient",
        back_populates="organization",
        cascade="all, delete"
    )