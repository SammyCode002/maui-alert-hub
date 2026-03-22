"""
Tsunami alert API endpoint.

GET /api/tsunami/  - Active tsunami alerts for Hawaii from NWS/PTWC
"""

import logging

from fastapi import APIRouter

from app.models.schemas import TsunamiResponse
from app.scrapers.tsunami_client import fetch_tsunami_alerts

logger = logging.getLogger("maui_alert_hub.api.tsunami")

router = APIRouter()


@router.get("/", response_model=TsunamiResponse)
async def get_tsunami_alerts():
    """
    Get active tsunami alerts for Hawaii from the National Weather Service.

    NWS distributes Pacific Tsunami Warning Center (PTWC) products through
    their standard alert API. This endpoint filters all Hawaii alerts for
    tsunami-specific event types.
    """
    return await fetch_tsunami_alerts()
