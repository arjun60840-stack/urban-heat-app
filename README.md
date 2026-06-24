# Urban Heat Analysis Platform

This is a full-stack application designed to analyze urban heat islands, recommend cooling interventions, and simulate their effects. Built with FastAPI (Backend) and Streamlit (Frontend).

## Phase 1: Project Setup

### Project Structure
- `backend/`: FastAPI server, database logic, and API endpoints.
- `frontend/`: Streamlit dashboard and user interface.
- `requirements.txt`: Python package dependencies.
- `.env`: Environment variables (API keys, DB config).

### Setup Instructions

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

2. **Activate Virtual Environment**
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Fill in your `GROQ_API_KEY` for the AI assistant module (Phase 8).

### Run Instructions

You will need two terminal windows (both with the virtual environment activated).

**Terminal 1: Start Backend (FastAPI)**
```bash
uvicorn backend.main:app --reload --port 8000
```
- API Docs will be available at: http://localhost:8000/docs

**Terminal 2: Start Frontend (Streamlit)**
```bash
streamlit run frontend/app.py
```
- Dashboard will be available at: http://localhost:8501
