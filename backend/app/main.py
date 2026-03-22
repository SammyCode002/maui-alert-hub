"""
Maui Alert Hub - FastAPI Backend
================================
Real-time road closures, weather alerts, and emergency info for Maui residents.

This is the main entry point. It sets up the FastAPI app, CORS, logging,
and registers all API routes.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.roads import router as roads_router
from app.api.weather import router as weather_router
from app.api.health import router as health_router
from app.api.earthquakes import router as earthquakes_router
from app.api.volcanic import router as volcanic_router
from app.api.surf import router as surf_router
from app.api.tsunami import router as tsunami_router
from app.api.aqi import router as aqi_router
from app.api.notifications import router as notifications_router
from app.api.community import router as community_router
from app.api.admin import router as admin_router
from app.scrapers.road_scraper import scrape_road_closures
from app.scrapers.dot_scraper import scrape_dot_closures
from app.scrapers.usgs_volcano_client import fetch_volcanic_alerts
from app.scrapers.noaa_buoy_client import fetch_surf_conditions
from app.scrapers.aqi_client import fetch_aqi
from app.database import init_db
from app.services.config import settings

scheduler = AsyncIOScheduler()


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
    Startup: warm road cache, start background scrape scheduler.
    Shutdown: stop scheduler, clean up resources.
    """
    logger.info("Starting Maui Alert Hub API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Scrape interval: {settings.scrape_interval_minutes} minutes")

    # Initialize database tables
    await init_db()

    # Warm all caches immediately on startup so first request is fast
    logger.info("Warming data caches on startup...")
    await asyncio.gather(
        scrape_road_closures(),
        scrape_dot_closures(),
        fetch_volcanic_alerts(),
        fetch_surf_conditions(),
        fetch_aqi(),
    )

    # Schedule periodic background scraping
    scheduler.add_job(
        scrape_road_closures, "interval",
        minutes=settings.scrape_interval_minutes, id="scrape_county",
    )
    scheduler.add_job(
        scrape_dot_closures, "interval",
        minutes=10, id="scrape_dot",
    )
    scheduler.add_job(
        fetch_volcanic_alerts, "interval",
        minutes=30, id="scrape_volcanic",
    )
    scheduler.add_job(
        fetch_surf_conditions, "interval",
        minutes=60, id="scrape_surf",
    )
    scheduler.add_job(
        fetch_aqi, "interval",
        minutes=60, id="scrape_aqi",
    )
    scheduler.start()
    logger.info(
        f"Scheduler started | county every {settings.scrape_interval_minutes}min "
        f"| DOT every 10min | volcanic every 30min | surf/aqi every 60min"
    )

    yield

    scheduler.shutdown()
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
app.include_router(earthquakes_router, prefix="/api/earthquakes", tags=["Earthquakes"])
app.include_router(volcanic_router, prefix="/api/volcanic", tags=["Volcanic"])
app.include_router(surf_router, prefix="/api/surf", tags=["Surf"])
app.include_router(tsunami_router, prefix="/api/tsunami", tags=["Tsunami"])
app.include_router(aqi_router, prefix="/api/aqi", tags=["AQI"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(community_router, prefix="/api/community-alerts", tags=["Community"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])


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
