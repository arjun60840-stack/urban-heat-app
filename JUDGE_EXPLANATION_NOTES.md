# 👨‍⚖️ Judge Explanation Notes (Cheat Sheet)

During the Q&A section of your hackathon, judges will grill you on your technical decisions and data sources. Use this cheat sheet to defend your architecture perfectly.

### Q1: "Where are you getting your temperature and coordinate data from?"
**Your Answer:** 
"To keep the platform globally scalable and completely free, we implemented a dual-API approach. First, we use **OpenStreetMap's Nominatim API** to geocode any city name into precise latitude/longitude coordinates. Then, we pass those coordinates into the **Open-Meteo API** to fetch real-time, live temperature data without needing API keys."

### Q2: "How does the 'What-If Simulator' actually calculate temperature drops?"
**Your Answer:**
"We built a localized cooling coefficient model based on urban forestry and materials research. 
- **Trees:** Each tree reduces ambient temperature by a micro-fraction through shade and evapotranspiration (we use `-0.001°C` per tree as a baseline).
- **Cool Roofs:** High-albedo surfaces reflect solar radiation. We calculate `-0.0005°C` per square meter of white roof installed.
The simulator dynamically multiplies user inputs by these coefficients to estimate realistic ROI."

### Q3: "Why did you use SQLite for the database?"
**Your Answer:**
"For the scope of an MVP and rapid hackathon prototyping, SQLite is the fastest way to get a persistent database running without network overhead. However, we used **SQLAlchemy** as our ORM. This means our database layer is completely abstracted. If we want to scale to a production PostgreSQL database on AWS or Supabase tomorrow, we literally only have to change one line of code: the `DATABASE_URL` environment variable."

### Q4: "How does the AI Assistant work?"
**Your Answer:**
"We wanted an AI that actually understands the city being analyzed, not just a generic chatbot. We integrated **Groq's API running the Llama 3 model**. When the user asks a question, our backend injects the current city's risk profile, average temperature, and hotspot data into the system prompt. This gives the AI 'context awareness' so it provides hyper-specific urban planning advice."

### Q5: "How are the Heatmap Hotspots generated?"
**Your Answer:**
"The engine takes the city's base temperature and applies a localized variance algorithm to simulate micro-climates. It clusters points around the city center, adding slight random offsets to the latitude/longitude and intensity to represent concrete traps versus greener suburbs."
