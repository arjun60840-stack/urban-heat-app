# 🎤 Presentation Notes (Solo Hacker)

**Pitch Angle:** Empowering local governments with data to fight climate change at the micro-level.

## The Hook (30 seconds)
- Start with a compelling stat: "Urban heat islands kill more people annually than any other weather-related event."
- Transition: "City planners don't lack motivation; they lack actionable intelligence. They don't know *where* to act, and *what* interventions actually work. Until now."

## The Demo (2 Minutes)
- **Show, don't tell.** Immediately pull up the Streamlit UI.
- Pick a famously hot city (e.g. Phoenix). Click Analyze.
- Watch the OpenStreetMap render the heat layer.
- Point to the specific generated Hotspots. "We found the exact block that needs help."
- Scroll to Recommendations: "Our engine doesn't just say 'it's hot'. It says 'plant 10,000 trees here to drop the temp by 1.2 degrees'."
- Play with the simulator sliders. "We can prove the ROI before breaking ground."
- Export the PDF Report.

## The AI Integration (1 Minute)
- "Instead of a static dashboard, I integrated Groq's Llama 3 API."
- "Planners can literally chat with their city data to ask about urban design standards or environmental impacts."

## Tech Stack (30 seconds)
- FastAPI (Speed & async routing)
- Streamlit (Rapid frontend prototyping)
- SQLAlchemy + SQLite
- FPDF (Report generation)
- Nominatim + Open-Meteo (Free geospatial & weather data)
- Groq (LLM Inference)

## Q&A Prep
- **"How are you getting the heat data?"** -> "I am geocoding cities using OpenStreetMap's Nominatim API, then fetching live temperature using Open-Meteo, and calculating localized spikes algorithmically to simulate micro-climates."
- **"How does the simulator work?"** -> "It uses a localized cooling coefficient model (e.g. -0.001C per tree) based on urban forestry studies."
