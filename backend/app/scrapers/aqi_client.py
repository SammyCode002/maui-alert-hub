"""
EPA AirNow air quality client for Maui Alert Hub.

Uses the EPA AirNow API (free, requires API key) to fetch current AQI
readings near Kahului, Maui. Returns PM2.5, O3, and other pollutant levels.

Particularly useful for vog (volcanic smog) advisories when Kilauea
or other Hawaii volcanoes are actively erupting — SO2 and PM2.5 spike
dramatically during high-vog conditions.

API docs: https://docs.airnow.gov/
"""

import logging
import time
from datetime import datetime
from typing import Optional

import httpx

from app.models.schemas import AQIReading, AQIResponse
from app.services.config import settings

logger = logging.getLogger("maui_alert_hub.aqi")

EPA_AIRNOW_BASE = "https://www.airnowapi.org/aq/observation/latLong/current/"

# Kahului, Maui — central monitoring point
MAUI_LAT = 20.8893
MAUI_LON = -156.4729
SEARCH_RADIUS_MILES = 50

# In-memory cache
_aqi_cache: Optional[AQIResponse] = None
_aqi_last_fetched: float = 0.0
_CACHE_TTL_SECONDS = 3600  # 1 hour — AirNow updates hourly

# AQI categories where vog advisory is warranted (Unhealthy and above)
VOG_ADVISORY_THRESHOLD = 3  # category_number >= 3 for PM2.5 or SO2


async def fetch_aqi() -> AQIResponse:
    """
    Fetch current AQI readings near Kahului, Maui from EPA AirNow.

    Returns cached data if fresh (< 1 hour old).
    Returns empty response if EPA_AQI_API_KEY is not configured.

    4x4 Logging: inputs (lat/lon), outputs (reading count), timing, status
    """
    global _aqi_cache, _aqi_last_fetched

    start_time = time.time()
    logger.info(f"INPUT  | fetch_aqi | lat={MAUI_LAT} lon={MAUI_LON}")

    if not settings.epa_aqi_api_key:
        logger.warning("OUTPUT | fetch_aqi | EPA_AQI_API_KEY not set | SKIP")
        return AQIResponse(readings=[], last_updated=datetime.now())

    # Serve from cache if fresh
    if _aqi_cache is not None and (time.time() - _aqi_last_fetched) < _CACHE_TTL_SECONDS:
        logger.info(f"OUTPUT | fetch_aqi | cached | count={len(_aqi_cache.readings)}")
        return _aqi_cache

    readings: list[AQIReading] = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                EPA_AIRNOW_BASE,
                params={
                    "format": "application/json",
                    "latitude": MAUI_LAT,
                    "longitude": MAUI_LON,
                    "distance": SEARCH_RADIUS_MILES,
                    "API_KEY": settings.epa_aqi_api_key,
                },
            )
            response.raise_for_status()
            data = response.json()

        for item in data:
            aqi_val = item.get("AQI", -1)
            if aqi_val < 0:
                continue  # -1 means no data available

            readings.append(AQIReading(
                parameter=item.get("ParameterName", "Unknown"),
                aqi=aqi_val,
                category=item.get("Category", {}).get("Name", "Unknown"),
                category_number=item.get("Category", {}).get("Number", 1),
                reporting_area=item.get("ReportingArea", "Maui"),
            ))

        # Sort: worst AQI first
        readings.sort(key=lambda r: r.aqi, reverse=True)

        # Flag vog advisory if PM2.5 or SO2 is Unhealthy for Sensitive Groups or worse
        is_vog = any(
            r.category_number >= VOG_ADVISORY_THRESHOLD
            and r.parameter.upper() in ("PM2.5", "SO2")
            for r in readings
        )

        result = AQIResponse(
            readings=readings,
            location="Maui, Hawaii",
            last_updated=datetime.now(),
            is_vog_advisory=is_vog,
        )
        _aqi_cache = result
        _aqi_last_fetched = time.time()

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | fetch_aqi | count={len(readings)} vog={is_vog} | "
            f"time={duration_ms:.1f}ms | OK"
        )
        return result

    except httpx.HTTPError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | fetch_aqi | error={e} | time={duration_ms:.1f}ms | ERROR"
        )
        if _aqi_cache is not None:
            return _aqi_cache
        return AQIResponse(readings=[], last_updated=datetime.now())
