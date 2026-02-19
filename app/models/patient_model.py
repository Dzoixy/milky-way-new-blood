from datetime import date
from sqlalchemy import String, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)  
full_name: Mapped[str] = mapped_column(String)  
national_id: Mapped[str] = mapped_column(String, unique=True)  
date_of_birth: Mapped[date] = mapped_column(Date)  
gender: Mapped[str] = mapped_column(String)  

visits = relationship("Visit", back_populates="patient")