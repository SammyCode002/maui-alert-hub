"""
Roads API endpoints.

GET /api/roads/        - List all current road closures/restrictions
GET /api/roads/refresh - Force a fresh scrape of county data
"""

import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, Request

from app.models.schemas import RoadResponse
from app.scrapers.road_scraper import get_cached_roads, scrape_road_closures
from app.scrapers.dot_scraper import get_cached_dot_roads, scrape_dot_closures
from app.services.push_service import check_and_notify_road_closures
from app.services.limiter import limiter, GENERAL

logger = logging.getLogger("maui_alert_hub.api.roads")

router = APIRouter()


@router.get("/", response_model=RoadResponse)
@limiter.limit(GENERAL)
async def get_road_closures(request: Request):
    """
    Get all current road closures and restrictions on Maui.

    Merges data from Maui County (emergency closures) and Hawaii DOT
    (lane closures / construction). Returns cached data if available,
    otherwise triggers a fresh scrape from both sources.
    """
    county_roads, county_scraped = get_cached_roads()
    dot_roads, dot_scraped = get_cached_dot_roads()

    if not county_roads and not dot_roads:
        logger.info("No cached road data, triggering fresh scrape from all sources")
        county_roads, dot_roads = await asyncio.gather(
            scrape_road_closures(),
            scrape_dot_closures(),
        )
        county_scraped = datetime.now()

    all_roads = county_roads + dot_roads
    last_scraped = county_scraped or dot_scraped

    # Check for new closures and notify subscribed users (deduped by seen_road_ids)
    if all_roads:
        await check_and_notify_road_closures(all_roads)

    return RoadResponse(
        roads=all_roads,
        total=len(all_roads),
        last_scraped=last_scraped,
    )


@router.get("/refresh", response_model=RoadResponse)
@limiter.limit(GENERAL)
async def refresh_road_closures(request: Request):
    """
    Force a fresh scrape from all sources (Maui County + Hawaii DOT).
    """
    logger.info("Manual road data refresh requested")
    county_roads, dot_roads = await asyncio.gather(
        scrape_road_closures(),
        scrape_dot_closures(),
    )
    all_roads = county_roads + dot_roads

    if all_roads:
        await check_and_notify_road_closures(all_roads)

    return RoadResponse(
        roads=all_roads,
        total=len(all_roads),
        last_scraped=datetime.now(),
    )
