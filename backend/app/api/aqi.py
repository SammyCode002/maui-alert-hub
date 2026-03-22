"""
Air Quality Index API endpoint.

GET /api/aqi/  - Current AQI readings for Maui from EPA AirNow
"""

import logging

from fastapi import APIRouter

from app.models.schemas import AQIResponse
from app.scrapers.aqi_client import fetch_aqi

logger = logging.getLogger("maui_alert_hub.api.aqi")

router = APIRouter()


@router.get("/", response_model=AQIResponse)
async def get_aqi():
    """
    Get current air quality readings for Maui from EPA AirNow.

    Returns PM2.5, O3, and other pollutant AQI values.
    The is_vog_advisory flag is set when PM2.5 or SO2 reaches
    Unhealthy for Sensitive Groups or worse (relevant during eruptions).

    Requires EPA_AQI_API_KEY env var. Returns empty list if not configured.
    """
    return await fetch_aqi()
