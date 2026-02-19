from sqlalchemy import Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.connection import Base

class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))

    sbp: Mapped[float]
    dbp: Mapped[float]
    risk_score: Mapped[float]

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    patient = relationship("Patient", back_populates="visits")