"""
Maui Alert Hub - FastAPI Backend
================================
Real-time road closures, weather alerts, and emergency info for Maui residents.

This is the main entry point. It sets up the FastAPI app, CORS, logging,
and registers all API routes.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.roads import router as roads_router
from app.api.weather import router as weather_router
from app.api.health import router as health_router
from app.services.config import settings


# ============================================================
# Logging Setup
# ============================================================
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("maui_alert_hub")


# ============================================================
# App Lifespan (startup/shutdown events)
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.
    Startup: log config, initialize scrapers.
    Shutdown: clean up resources.
    """
    logger.info("Starting Maui Alert Hub API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Scrape interval: {settings.scrape_interval_minutes} minutes")
    yield
    logger.info("Shutting down Maui Alert Hub API")


# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(
    title="Maui Alert Hub API",
    description="Real-time road closures, weather alerts, and emergency info for Maui.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: allow the React frontend to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 4x4 Debug Logging Middleware
# Logs: input (request), output (status), timing, status for every request
# ============================================================
@app.middleware("http")
async def debug_logging_middleware(request: Request, call_next):
    """Log every request with 4x4 pattern: input, output, timing, status."""
    start_time = time.time()

    # INPUT: Log the incoming request
    logger.debug(
        f"INPUT  | {request.method} {request.url.path} | "
        f"query={dict(request.query_params)}"
    )

    # Process the request
    response = await call_next(request)

    # TIMING + OUTPUT + STATUS
    duration_ms = (time.time() - start_time) * 1000
    logger.debug(
        f"OUTPUT | {request.method} {request.url.path} | "
        f"status={response.status_code} | "
        f"time={duration_ms:.1f}ms | "
        f"{'OK' if response.status_code < 400 else 'ERROR'}"
    )

    return response


# ============================================================
# Register API Routes
# ============================================================
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(roads_router, prefix="/api/roads", tags=["Roads"])
app.include_router(weather_router, prefix="/api/weather", tags=["Weather"])


# ============================================================
# Root Redirect
# ============================================================
@app.get("/")
async def root():
    """Root endpoint. Points users to the API docs."""
    return {
        "app": "Maui Alert Hub API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }
