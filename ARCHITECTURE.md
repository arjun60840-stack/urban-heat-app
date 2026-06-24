# 🏗️ Architecture Diagram

```mermaid
graph TD
    A[User / City Planner] -->|Interacts with| B[Streamlit Frontend UI]
    B -->|REST API Calls| C[FastAPI Backend]
    
    subaxis
    C -->|GET /analyze-city| D[OpenStreetMap Geocoding]
    C -->|GET /weather| E[Open-Meteo API]
    C -->|POST /chat| F[Groq API / Llama 3]
    end

    C -->|Reads/Writes| G[(SQLite Database)]
    C -->|Generates| H[PDF Reports via FPDF]
    
    subgraph Backend Routers
    C1(Analysis Router)
    C2(Interventions Router)
    C3(AI Router)
    C4(Reports Router)
    end
```

## Key Components:
- **Frontend**: Streamlit + Folium (Map rendering, Charting, UI components)
- **Backend**: FastAPI + Pydantic + SQLAlchemy (Data validation, routing, DB ORM)
- **Database**: SQLite (local testing, easily swappable to PostgreSQL)
- **External Services**: 
  - Nominatim (Geocoding)
  - Open-Meteo (Weather Data)
  - Groq (LLM Inference)
