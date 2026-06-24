from pydantic import BaseModel
from typing import List, Optional, Any

class CityRequest(BaseModel):
    city_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class HeatMapResponse(BaseModel):
    city_name: str
    heatmap_data: List[dict]

class RecommendationRequest(BaseModel):
    city_name: str
    risk_category: str

class SimulateRequest(BaseModel):
    city_name: str
    trees_added: int = 0
    cool_roofs_area: float = 0.0
    new_water_bodies: int = 0

class PredictRequest(BaseModel):
    city_name: str
    months_ahead: int = 1

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class ReportRequest(BaseModel):
    city_name: str
    data_summary: dict
