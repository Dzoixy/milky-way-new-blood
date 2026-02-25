from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.connection import Base


class Visit(Base):
    __tablename__ = "visits"

    # ==========================
    # Primary Key
    # ==========================
    id = Column(Integer, primary_key=True, index=True)

    # ==========================
    # Foreign Keys
    # ==========================
    patient_id = Column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # ==========================
    # Vital Signs
    # ==========================
    systolic_bp = Column(Integer, nullable=False)
    diastolic_bp = Column(Integer, nullable=False)
    fasting_glucose = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)

    # ==========================
    # Lifestyle
    # ==========================
    smoking = Column(String(50), nullable=True)
    alcohol = Column(String(50), nullable=True)

    # ==========================
    # Medical History
    # ==========================
    chronic_diseases = Column(Text, nullable=True)
    family_history = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # ==========================
    # Risk Engine
    # ==========================
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)

    # ==========================
    # Metadata
    # ==========================
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ==========================
    # Relationships
    # ==========================
    patient = relationship(
        "Patient",
        back_populates="visits"
    )

    organization = relationship(
        "Organization"
    )