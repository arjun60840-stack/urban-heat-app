import os
from fastapi import APIRouter
from .. import schemas
from ..logger import logger
import random

router = APIRouter(prefix="/ai", tags=["AI & Prediction"])

@router.post("/predict")
def predict_future_heat(request: schemas.PredictRequest):
    logger.info(f"Predicting future heat for {request.city_name} {request.months_ahead} months ahead")
    
    # Simple seasonal mock prediction
    base_temp = 30.0
    forecast = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for i in range(request.months_ahead):
        month_idx = i % 12
        # Summer months are hotter
        if 4 <= month_idx <= 8:
            temp = base_temp + random.uniform(5, 10)
        else:
            temp = base_temp - random.uniform(0, 10)
            
        forecast.append({"month": f"{months[month_idx]}", "predicted_avg_temp": round(temp, 1)})
        
    return {
        "city_name": request.city_name,
        "forecast": forecast
    }

@router.post("/chat")
def chat_with_assistant(request: schemas.ChatRequest):
    logger.info("Received chat message for AI assistant")
    api_key = os.getenv("GROQ_API_KEY")
    
    prompt = f"Context: {request.context}\nUser: {request.message}\nProvide a short, helpful response as an Urban Planning AI."
    
    if api_key and api_key != "your_groq_api_key_here":
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            return {"response": completion.choices[0].message.content}
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {"response": f"AI Assistant (Fallback): I received your message '{request.message}'. (Groq API failed)."}
    else:
        return {"response": f"AI Assistant (Mock Mode): You asked '{request.message}'. To get real AI responses, add your GROQ_API_KEY to the .env file!"}

