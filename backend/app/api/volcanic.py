"""Volcanic activity endpoint — GET /api/volcanic/"""

import logging
from datetime import datetime

from fastapi import APIRouter, Request

from app.models.schemas import VolcanicResponse
from app.scrapers.usgs_volcano_client import fetch_volcanic_alerts, get_cached_volcanic_alerts
from app.services.limiter import limiter, GENERAL

logger = logging.getLogger("maui_alert_hub.api.volcanic")
router = APIRouter()


@router.get("/", response_model=VolcanicResponse)
@limiter.limit(GENERAL)
async def get_volcanic_alerts(request: Request):
    """
    Get current volcanic activity notifications for Hawaii volcanoes from USGS.

    Covers Kīlauea, Mauna Loa, Haleakalā, and other Hawaiian volcanoes.
    Returns cached data if a fresh fetch fails.
    """
    cached, last_fetched = get_cached_volcanic_alerts()

    if not cached:
        alerts = await fetch_volcanic_alerts()
    else:
        alerts = cached

    return VolcanicResponse(
        alerts=alerts,
        total=len(alerts),
        last_updated=last_fetched or datetime.now(),
    )
