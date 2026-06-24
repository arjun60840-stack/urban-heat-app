# 🏆 Urban Heat App: Hackathon Demo Guide

This guide is designed to help you crush your hackathon presentation.

## The Problem
"Urban heat islands are making our cities unlivable. Concrete traps heat, causing massive spikes in temperature that impact health and energy consumption. Planners need data-driven tools to fight this."

## The Solution
"We built the **Urban Heat Intelligence Platform**, a full-stack solution that not only visualizes heat but acts as an AI City Planner to simulate interventions."

## 🎥 Live Demo Flow

1. **Start at the Search Screen**
   - Type in a notoriously hot city, like "Phoenix" or "Dubai".
   - *Talking point:* "We use live geocoding to find any city and pull real-time weather data."

2. **The Map & Hotspots**
   - Show the interactive map.
   - *Talking point:* "The heat map dynamically generates based on temperature data, and our algorithm automatically flags extreme risk hotspots (e.g., Downtown Concrete Core)."

3. **Recommendation Engine**
   - Scroll down to the cooling recommendations.
   - *Talking point:* "Based on the exact risk category, our engine prescribes targeted solutions—like adding tree canopies or cool roofs—along with their precise environmental impact."

4. **What-If Simulator**
   - Adjust the sliders for Trees, Cool Roofs, and Parks.
   - *Talking point:* "City planners can simulate ROI. By sliding these toggles, we can predict exactly how many degrees of cooling we achieve."

5. **Future Heat Prediction**
   - Point to the line chart.
   - *Talking point:* "We forecast the temperature trend over the next 12 months so cities can prepare for seasonal extremes."

6. **AI Assistant & PDF Export**
   - Ask the AI a question: "How does white paint cool buildings?"
   - Click 'Generate PDF Report'.
   - *Talking point:* "Finally, our Groq-powered Llama 3 AI is ready to answer specific planning questions, and we can export all this intelligence into a PDF report for city council meetings."

## Technical Flex for the Judges
- Built in **Python** using **FastAPI** for a lightning-fast backend.
- UI built with **Streamlit** and interactive GIS maps via **Folium**.
- Database ready with **SQLAlchemy/SQLite**.
- Integrated **OpenStreetMap**, **Open-Meteo**, and **Groq AI (Llama 3)**.
