from datetime import datetime
from sqlalchemy import Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Clinical measurements
    sbp: Mapped[float] = mapped_column(Float, nullable=False)
    dbp: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    patient = relationship(
        "Patient",
        back_populates="visits"
    )

    risk_result = relationship(
        "RiskResult",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan"
    )