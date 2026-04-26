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
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

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
from app.database import init_db, engine
from app.services.config import settings
from app.services.limiter import limiter

scheduler = AsyncIOScheduler()

# Per-scraper timeout for the initial warmup gather. Beyond this,
# the scraper is logged as timed out and the rest of startup continues.
WARMUP_TIMEOUT_S = 30


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
# Cache warmup helpers
# ============================================================
async def _warm_one(name: str, fn, timeout_s: int = WARMUP_TIMEOUT_S) -> None:
    """
    Run a single warmup scraper with a hard timeout and exception capture.

    WHY: A hung external API (NWS, USGS, county site) used to stall the entire
    startup gather, which kept /api/health unreachable for minutes and tripped
    UptimeRobot. Wrapping each scraper in wait_for plus try/except lets one
    bad source fail loudly without blocking the rest.

    Args:
        name: Scraper label for logs.
        fn: Async callable with no args.
        timeout_s: Max seconds before the scraper is abandoned.
    """
    start = time.time()
    try:
        await asyncio.wait_for(fn(), timeout=timeout_s)
        logger.info(f"warmup ok | {name} | {time.time() - start:.2f}s")
    except asyncio.TimeoutError:
        logger.warning(f"warmup timeout | {name} | gave up after {timeout_s}s")
    except Exception as exc:
        logger.error(
            f"warmup failed | {name} | {time.time() - start:.2f}s | {exc}",
            exc_info=True,
        )


async def _warm_all_caches() -> None:
    """
    Run all initial scrapers in parallel as a background task.

    Fired with asyncio.create_task during lifespan startup so the API is
    immediately ready to serve /api/health while caches populate behind it.
    First page loads after a cold start may briefly show empty data, then
    populate as each scraper completes.
    """
    logger.info("background cache warmup started")
    start = time.time()
    await asyncio.gather(
        _warm_one("road_closures", scrape_road_closures),
        _warm_one("dot_closures", scrape_dot_closures),
        _warm_one("volcanic", fetch_volcanic_alerts),
        _warm_one("surf", fetch_surf_conditions),
        _warm_one("aqi", fetch_aqi),
        return_exceptions=True,
    )
    logger.info(f"background cache warmup complete | {time.time() - start:.2f}s")


# ============================================================
# App Lifespan (startup/shutdown events)
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.
    Startup: init DB, fire scrapers in background, start scheduler.
    Shutdown: stop scheduler, clean up resources.

    NOTE: Scrapers used to run via blocking asyncio.gather here, which delayed
    /api/health for minutes during cold starts. They now run as a background
    task so health responds immediately and Render's healthCheck does not fail.
    """
    logger.info("Starting Maui Alert Hub API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Scrape interval: {settings.scrape_interval_minutes} minutes")

    # Initialize database tables
    await init_db()

    # Fire warmup in the background so startup does not block on external APIs
    asyncio.create_task(_warm_all_caches())

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
    await engine.dispose()
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

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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
