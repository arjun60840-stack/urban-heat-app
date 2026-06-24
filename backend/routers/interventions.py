from fastapi import APIRouter, HTTPException
from .. import schemas
from ..logger import logger

router = APIRouter(prefix="/interventions", tags=["Interventions"])

@router.post("/recommendations")
def get_recommendations(request: schemas.RecommendationRequest):
    logger.info(f"Generating recommendations for {request.city_name} with risk {request.risk_category}")
    recs = []
    
    if request.risk_category == "Extreme":
        recs.append({
            "type": "Cool Roofs", 
            "impact": "High", 
            "cooling_effect_celsius": 1.5,
            "environmental_impact": "Reflects solar radiation, reducing building energy use by up to 20%.",
            "details": "Mandate high-albedo (white) paint on all commercial flat roofs."
        })
        recs.append({
            "type": "Water Bodies", 
            "impact": "High", 
            "cooling_effect_celsius": 2.0,
            "environmental_impact": "Evaporative cooling lowers ambient temperature in a 1km radius.",
            "details": "Construct artificial lakes or misting plazas in the highest risk zones."
        })
    elif request.risk_category == "High":
        recs.append({
            "type": "Tree Plantation", 
            "impact": "Medium-High", 
            "cooling_effect_celsius": 1.2,
            "environmental_impact": "Increases shade and transpirational cooling; absorbs CO2.",
            "details": "Plant 10,000 broad-leaf native trees along major asphalt corridors."
        })
        recs.append({
            "type": "Green Roofs", 
            "impact": "Medium", 
            "cooling_effect_celsius": 0.8,
            "environmental_impact": "Reduces stormwater runoff and provides habitat for urban wildlife.",
            "details": "Incentivize rooftop vegetation and gardens on residential buildings."
        })
    else: # Medium or Low
        recs.append({
            "type": "Urban Parks", 
            "impact": "Medium", 
            "cooling_effect_celsius": 1.0,
            "environmental_impact": "Reduces concrete surface area and creates micro-climates.",
            "details": "Convert 5 vacant city lots into neighborhood pocket parks."
        })
        recs.append({
            "type": "Tree Plantation", 
            "impact": "Low", 
            "cooling_effect_celsius": 0.5,
            "environmental_impact": "Maintains existing air quality and shade canopy.",
            "details": "Maintain existing street trees and increase overall canopy coverage by 5%."
        })
        
    return {"city_name": request.city_name, "recommendations": recs}

@router.post("/simulate")
def simulate_interventions(request: schemas.SimulateRequest):
    logger.info(f"Simulating interventions for {request.city_name}")
    # Mock simulation (to be expanded in Phase 6)
    temp_reduction = (request.trees_added * 0.001) + (request.cool_roofs_area * 0.0005)
    return {
        "city_name": request.city_name,
        "predicted_temp_reduction_celsius": round(temp_reduction, 2),
        "improvement_score": min(100, int(temp_reduction * 20))
    }

