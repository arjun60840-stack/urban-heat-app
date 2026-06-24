from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from . import database
from .logger import logger
from .routers import analysis, interventions, ai, reports

# Initialize database tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Urban Heat Analysis API",
    description="API for analyzing urban heat islands and simulating cooling interventions.",
    version="1.0.0"
)

# Mount static files for reports
os.makedirs("static/reports", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred.", "details": str(exc)},
    )

# Include Routers
app.include_router(analysis.router)
app.include_router(interventions.router)
app.include_router(ai.router)
app.include_router(reports.router)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Urban Heat Analysis API. Visit /docs for documentation."}

@app.get("/health")
def health_check():
    return {"status": "ok"}
