from datetime import date
from sqlalchemy import String, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    national_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    gender: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # ==========================
    # Relationships
    # ==========================

    user = relationship("User")

    organization = relationship(
        "Organization",
        back_populates="patients"
    )

    visits = relationship(
        "Visit",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    # ==========================
    # SaaS Unique Constraint
    # ==========================

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "national_id",
            name="uq_patient_org_nid"
        ),
    )