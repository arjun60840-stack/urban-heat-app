import requests
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, database
from ..logger import logger

router = APIRouter(prefix="/analysis", tags=["Analysis"])

def geocode_city(city_name: str):
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    headers = {"User-Agent": "UrbanHeatApp/1.0"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and len(res.json()) > 0:
            data = res.json()[0]
            return float(data["lat"]), float(data["lon"])
    except Exception as e:
        logger.error(f"Geocoding failed: {e}")
    return None, None

def fetch_temperature(lat: float, lon: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json().get("current_weather", {}).get("temperature", 30.0)
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
    return 30.0

def calculate_risk(temp: float):
    if temp < 30: return "Low"
    elif temp < 35: return "Medium"
    elif temp < 40: return "High"
    return "Extreme"

@router.post("/analyze-city")
def analyze_city(request: schemas.CityRequest, db: Session = Depends(database.get_db)):
    logger.info(f"Analyzing city: {request.city_name}")
    
    lat, lon = geocode_city(request.city_name)
    if not lat:
        lat, lon = 40.7128, -74.0060 # Fallback NYC

    temp = fetch_temperature(lat, lon)
    risk = calculate_risk(temp)
    
    db_analysis = models.CityAnalysis(
        city_name=request.city_name,
        latitude=lat,
        longitude=lon,
        avg_temperature=temp,
        risk_category=risk
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return {"status": "success", "data": db_analysis}

@router.get("/heat-map")
def get_heat_map(city_name: str):
    logger.info(f"Fetching heat map for: {city_name}")
    lat, lon = geocode_city(city_name)
    if not lat:
        lat, lon = 40.7128, -74.0060
        
    temp = fetch_temperature(lat, lon)
    
    # Generate heat map points based on base temperature
    heatmap_data = []
    for _ in range(30):
        lat_offset = random.uniform(-0.06, 0.06)
        lon_offset = random.uniform(-0.06, 0.06)
        intensity = min(1.0, (temp + random.uniform(-5, 5)) / 45.0)
        
        heatmap_data.append({
            "lat": lat + lat_offset,
            "lon": lon + lon_offset,
            "intensity": max(0.2, intensity)
        })
        
    return {
        "city_name": city_name,
        "heatmap_data": heatmap_data
    }

@router.get("/hotspots")
def get_hotspots(city_name: str):
    logger.info(f"Fetching hotspots for: {city_name}")
    lat, lon = geocode_city(city_name)
    if not lat:
        lat, lon = 40.7128, -74.0060
    
    temp = fetch_temperature(lat, lon)
    risk = calculate_risk(temp)
    
    return {
        "city_name": city_name,
        "base_temperature": temp,
        "overall_risk": risk,
        "hotspots": [
            {"name": "Downtown Concrete Core", "estimated_temp": round(temp + 3.2, 1), "risk": calculate_risk(temp + 3.2)},
            {"name": "Industrial Sector", "estimated_temp": round(temp + 2.5, 1), "risk": calculate_risk(temp + 2.5)},
            {"name": "Residential Suburbs", "estimated_temp": round(temp - 1.5, 1), "risk": calculate_risk(temp - 1.5)}
        ]
    }

