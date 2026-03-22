"""
Roads API endpoints.

GET /api/roads/        - List all current road closures/restrictions
GET /api/roads/refresh - Force a fresh scrape of county data
"""

import logging
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import RoadResponse
from app.scrapers.road_scraper import get_cached_roads, scrape_road_closures

logger = logging.getLogger("maui_alert_hub.api.roads")

router = APIRouter()


@router.get("/", response_model=RoadResponse)
async def get_road_closures():
    """
    Get all current road closures and restrictions on Maui.

    Returns cached data if available, otherwise triggers a fresh scrape.
    The scraper runs on a schedule, so this usually returns fast from cache.
    """
    roads, last_scraped = get_cached_roads()

    # If we have no cached data, do a fresh scrape
    if not roads:
        logger.info("No cached road data, triggering fresh scrape")
        roads = await scrape_road_closures()
        last_scraped = datetime.now()

    return RoadResponse(
        roads=roads,
        total=len(roads),
        last_scraped=last_scraped,
    )


@router.get("/refresh", response_model=RoadResponse)
async def refresh_road_closures():
    """
    Force a fresh scrape of road closure data.

    Use this when you want the absolute latest data.
    Note: Please don't call this every second, the county site has limits.
    """
    logger.info("Manual road data refresh requested")
    roads = await scrape_road_closures()

    return RoadResponse(
        roads=roads,
        total=len(roads),
        last_scraped=datetime.now(),
    )
