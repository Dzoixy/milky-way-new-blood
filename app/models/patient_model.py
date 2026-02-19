from datetime import date
from sqlalchemy import String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    national_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)

    visits = relationship("Visit", back_populates="patient", cascade="all, delete-orphan")