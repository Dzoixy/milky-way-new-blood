from datetime import datetime
from sqlalchemy import Float, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class RiskResult(Base):
    __tablename__ = "risk_results"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    visit_id: Mapped[int] = mapped_column(
        ForeignKey("visits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # 1 visit = 1 risk result
        index=True
    )

    risk_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    full_json: Mapped[dict] = mapped_column(
        JSONB,   # PostgreSQL optimized
        nullable=False
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    visit = relationship(
        "Visit",
        back_populates="risk_result"
    )