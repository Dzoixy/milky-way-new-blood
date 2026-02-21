from sqlalchemy import Column, Integer, Float, String, ForeignKey, JSON
from app.database.connection import Base

class RiskResult(Base):
    __tablename__ = "risk_results"

    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"))
    risk_percent = Column(Float)
    category = Column(String)
    full_json = Column(JSON)