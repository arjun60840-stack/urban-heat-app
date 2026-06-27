# 🚀 Production Deployment Guide

When you are ready to take your Urban Heat Intelligence Platform out of `localhost` and put it on the public internet, follow this guide.

## Recommended Free-Tier Stack
Since you are optimizing for free services, we recommend the following stack:
1. **Backend API (FastAPI)**: Deploy to [Render.com](https://render.com) (Free Tier)
2. **Frontend UI (Streamlit)**: Deploy to [Streamlit Community Cloud](https://share.streamlit.io/) (Free forever)
3. **Database**: Use a free managed PostgreSQL database on [Supabase](https://supabase.com) or [Neon.tech](https://neon.tech) instead of SQLite.

---

## Step 1: Prepare the Repository
1. Initialize a Git repository in your folder.
2. Push the code to a public or private GitHub repository.
3. Make sure your `requirements.txt` is updated.

---

## Step 2: Deploy the Backend (Render)
1. Go to Render.com and create a **Web Service**.
2. Connect your GitHub repository.
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   - `DATABASE_URL`: Add your Supabase/Neon PostgreSQL URL here.
   - `GROQ_API_KEY`: Add your secret Groq key here.
   - `SECRET_API_KEY`: Add a strong random key here (used for API authentication).

---

## Step 3: Deploy the Frontend (Streamlit Cloud)
1. Go to Streamlit Community Cloud.
2. Click **New app** and select your GitHub repository.
3. **Main file path**: `frontend/app.py`
4. *Important Code Change:* Once your backend is live on Render, you must update the URLs in `frontend/app.py` from `http://localhost:8000` to your new Render URL (e.g., `https://urban-heat-api.onrender.com`).
5. **Secrets**: In Streamlit Cloud settings, add `SECRET_API_KEY` with the same value as on Render.
6. Click **Deploy**.

---

## Step 4: Database Migrations (Alembic)

Alembic manages your database schema changes so you never have to manually edit tables.

### Initial Setup (First Time)
```bash
# Install Alembic (included in requirements-dev.txt)
pip install -r requirements-dev.txt

# Apply all migrations to bring the DB up to date
alembic upgrade head
```

### Creating New Migrations
When you add or change models in `backend/models.py`:
```bash
# Auto-generate a migration script from model changes
alembic revision --autogenerate -m "describe your change"

# Review the generated file in alembic/versions/
# Then apply it
alembic upgrade head
```

### Useful Commands
```bash
alembic current           # Show current migration revision
alembic history           # Show full migration history
alembic downgrade -1      # Roll back the last migration
alembic upgrade head      # Apply all pending migrations
```

### Production Note
Set the `DATABASE_URL` environment variable before running migrations against your production database:
```bash
DATABASE_URL=postgresql://user:pass@host/db alembic upgrade head
```

---

## Step 5: Docker Deployment (Alternative)

You can also deploy the full stack using Docker:

```bash
# Build and start both services
docker compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

Make sure your `.env` file has all required variables:
```
GROQ_API_KEY=your_key
DATABASE_URL=sqlite:///./urban_heat.db
SECRET_API_KEY=your_secret_key
```

---

Your app is now live and ready to be judged!
