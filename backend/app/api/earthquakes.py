"""
Earthquake API endpoint.

GET /api/earthquakes/ - Get recent earthquakes near Maui (all main Hawaiian Islands)
"""

import logging
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import EarthquakeResponse
from app.scrapers.usgs_client import fetch_earthquakes

logger = logging.getLogger("maui_alert_hub.api.earthquakes")

router = APIRouter()


@router.get("/", response_model=EarthquakeResponse)
async def get_earthquakes():
    """
    Get recent earthquakes within 300km of Maui from the USGS.

    Covers all main Hawaiian Islands. Returns up to 10 earthquakes
    ordered by most recent first. Minimum magnitude 2.5.
    """
    earthquakes = await fetch_earthquakes()
    return EarthquakeResponse(
        earthquakes=earthquakes,
        total=len(earthquakes),
        last_updated=datetime.now(),
    )
