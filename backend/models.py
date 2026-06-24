from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime
from .database import Base

class CityAnalysis(Base):
    __tablename__ = "city_analysis"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    avg_temperature = Column(Float)
    risk_category = Column(String) # Low, Medium, High, Extreme
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
