"""Surf conditions endpoint — GET /api/surf/"""

import logging
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import SurfResponse
from app.scrapers.noaa_buoy_client import fetch_surf_conditions, get_cached_surf

logger = logging.getLogger("maui_alert_hub.api.surf")
router = APIRouter()


@router.get("/", response_model=SurfResponse)
async def get_surf():
    """
    Get current surf conditions from NOAA NDBC buoys near Maui.

    Buoys: Pauwela (north Maui) and NW Hawaii offshore.
    Wave heights in feet, water temp in Fahrenheit.
    Data updates hourly from NOAA.
    """
    cached, last_fetched = get_cached_surf()

    if not cached:
        spots = await fetch_surf_conditions()
    else:
        spots = cached

    return SurfResponse(
        spots=spots,
        last_updated=last_fetched or datetime.now(),
    )
