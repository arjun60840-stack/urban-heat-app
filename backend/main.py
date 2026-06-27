from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from . import database
from .logger import logger
from .routers import analysis, interventions, ai, reports

# Initialize database tables
database.Base.metadata.create_all(bind=database.engine)

# --- Rate Limiter Setup ---
# 30 requests per minute per IP address
limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])


# --- API Key Middleware ---
# Validates X-API-Key header on all requests except public paths.
class APIKeyMiddleware(BaseHTTPMiddleware):
    # Paths that do not require an API key
    PUBLIC_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        secret_key = os.getenv("SECRET_API_KEY")

        # If no SECRET_API_KEY is configured, skip validation entirely
        # (allows local development without setting the key)
        if not secret_key:
            return await call_next(request)

        # Allow public endpoints without a key
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Check for the API key header
        provided_key = request.headers.get("X-API-Key")
        if provided_key != secret_key:
            logger.warning(f"Unauthorized request to {request.url.path} from {request.client.host}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized. Provide a valid X-API-Key header."}
            )

        return await call_next(request)


app = FastAPI(
    title="Urban Heat Analysis API",
    description="API for analyzing urban heat islands and simulating cooling interventions.",
    version="1.0.0"
)

# Attach rate limiter to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Attach API key middleware
app.add_middleware(APIKeyMiddleware)

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
