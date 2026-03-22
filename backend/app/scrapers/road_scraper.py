"""
Maui County road closure scraper.

Scrapes road closure information from the Maui County website.
Since the county doesn't have a public API, we parse their HTML pages.

IMPORTANT: We scrape responsibly:
- Rate limited (default: every 5 minutes, not every second)
- Cached results so we don't hammer their server
- Proper User-Agent header identifying our app

TODO (Phase 2): Replace scraping with official data if/when county provides an API.
"""

import logging
import re
import time
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.models.schemas import RoadClosure, RoadStatus

logger = logging.getLogger("maui_alert_hub.road_scraper")

# Maui County road closure page
MAUI_COUNTY_URL = "https://www.mauicounty.gov"

# In-memory cache (keeps results between scrapes)
_road_cache: list[RoadClosure] = []
_last_scraped: Optional[datetime] = None


async def scrape_road_closures() -> list[RoadClosure]:
    """
    Scrape current road closures from Maui County website.

    For the MVP, we start with some known, manually-entered closures
    and supplement with scraped data. As we learn the county site's
    HTML structure, we'll improve the parser.

    4x4 Logging: inputs (URL), outputs (closure count), timing, status
    """
    global _road_cache, _last_scraped

    start_time = time.time()
    logger.info(f"INPUT  | scrape_road_closures | url={MAUI_COUNTY_URL}")

    closures = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                MAUI_COUNTY_URL,
                headers={"User-Agent": "MauiAlertHub/1.0"},
                follow_redirects=True,
            )
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Look for road closure alerts in the page
        # The county site uses CivicAlerts and various notification divs
        # This parser will evolve as we learn the HTML structure
        alert_elements = soup.find_all(
            "a", string=lambda text: text and any(
                keyword in text.upper()
                for keyword in ["ROAD CLOSURE", "ROAD", "HIGHWAY", "CLOSED"]
            )
        )

        i = 0
        for element in alert_elements:
            text = element.get_text(strip=True)
            if not _is_valid_closure(text):
                logger.debug(f"SKIP   | filtered nav/junk link: {text[:60]}")
                continue
            closure = RoadClosure(
                id=f"county-{i}",
                road_name=_extract_road_name(text),
                status=_determine_status(text),
                description=text,
                location=_extract_location(text),
                source="Maui County",
                updated_at=datetime.now(),
            )
            closures.append(closure)
            i += 1

        # Update cache
        _road_cache = closures
        _last_scraped = datetime.now()

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | scrape_road_closures | count={len(closures)} | "
            f"time={duration_ms:.1f}ms | OK"
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | scrape_road_closures | error={str(e)} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )
        # Return cached data if scrape fails
        return _road_cache

    return closures


def get_cached_roads() -> tuple[list[RoadClosure], Optional[datetime]]:
    """Return cached road data and when it was last scraped."""
    return _road_cache, _last_scraped


def _is_valid_closure(text: str) -> bool:
    """
    Filter out navigation links and non-closure text scraped from the county site.

    Returns True only for genuine road closure/update entries.
    """
    text = text.strip()
    # Skip generic nav/subscribe links like "Road Closure Notifications"
    if re.match(r'(?i)^(subscribe\s+to\s+)?road\s+closure\s+notifications?$', text):
        return False
    # Must match at least one known closure pattern to be considered valid
    has_pattern = bool(
        re.match(r'(?i)road\s+closure:', text)
        or re.search(r'(?i)\bfor\s+\S.+\s+on\s+', text)
        or re.match(r'(?i)\*+\s*update', text)
    )
    return has_pattern


def _extract_road_name(text: str) -> str:
    """
    Extract the road name from a county alert string.

    Handles three real-world county formats:
      - "Road Closure: Lono Ave / W Kamehameha Ave"
      - "Road Closure: Kuihelani Hwy between Maui Lani Pkwy to Honoapiilani Hwy"
      - "ROAD CLOSURE: 03/22/26 AT 8:19 AM FOR KAMEHAMEHA V HIGHWAY ON MOLOKA'I"
      - "**UPDATE LOWER KULA ROAD ** 03/22/26 AT 6:12 AM **"
    """
    text = text.strip()

    # Pattern: "... FOR {road} ON {location}" (all-caps county date format)
    m = re.search(r'(?i)\bfor\s+(.+?)\s+on\s+\S', text)
    if m:
        return m.group(1).strip().title()

    # Pattern: "**UPDATE {road} **..."
    m = re.match(r'(?i)\*+\s*update\s+(.+?)\s*\*+', text)
    if m:
        return m.group(1).strip().title()

    # Pattern: "Road Closure: {road} [in/between ...]"
    m = re.match(r'(?i)road\s+closure:\s*(.+?)(?:\s+(?:in|between)\s+.+)?$', text)
    if m:
        name = m.group(1).strip()
        if name:
            return name  # Keep county's original casing (already title-case)

    return "Unknown Road"


def _determine_status(text: str) -> RoadStatus:
    """Determine road status from alert text."""
    text_upper = text.upper()
    if "CLOSED" in text_upper or "CLOSURE" in text_upper:
        return RoadStatus.CLOSED
    elif "LOCAL" in text_upper or "RESTRICTED" in text_upper or "ONLY" in text_upper:
        return RoadStatus.RESTRICTED
    elif "OPEN" in text_upper:
        return RoadStatus.OPEN
    return RoadStatus.UNKNOWN


def _extract_location(text: str) -> Optional[str]:
    """
    Extract the specific location detail from a county alert string.

    Handles patterns like:
      - "Road Closure: road between {location}"
      - "Road Closure: road in {location}"
      - "... FOR road ON {location}"
    """
    text = text.strip()

    # "Road Closure: road between {location}"
    m = re.match(r'(?i)road\s+closure:\s*.+?\s+between\s+(.+)$', text)
    if m:
        return m.group(1).strip()[:100]

    # "Road Closure: road in {location}"
    m = re.match(r'(?i)road\s+closure:\s*.+?\s+in\s+(.+)$', text)
    if m:
        return m.group(1).strip()[:100]

    # "... FOR road ON {location}"
    m = re.search(r'(?i)\bon\s+(\w.+?)$', text)
    if m:
        return m.group(1).strip().title()[:100]

    return None
