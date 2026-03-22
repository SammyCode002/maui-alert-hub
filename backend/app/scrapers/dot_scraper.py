"""
Hawaii DOT Maui lane closure scraper.

Scrapes lane closure data from the Hawaii Department of Transportation Maui page.
DOT data is different from county closures:
  - DOT  = lane closures (construction work, RESTRICTED status)
  - County = emergency road closures (accidents/events, CLOSED status)

Both sources are merged in the roads dashboard.

DOT Maui page: https://hidot.hawaii.gov/highways/roadwork/maui/
The page uses paragraph-based CMS content with no structured containers,
so we parse <p> tags that contain lane/road closure keywords.
"""

import logging
import re
import time
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.models.schemas import RoadClosure, RoadStatus

logger = logging.getLogger("maui_alert_hub.dot_scraper")

DOT_MAUI_URL = "https://hidot.hawaii.gov/highways/roadwork/maui/"

# In-memory cache
_dot_cache: list[RoadClosure] = []
_dot_last_scraped: Optional[datetime] = None

# Keywords that indicate a genuine closure/restriction entry
_CLOSURE_KEYWORDS = [
    "lane closed",
    "lane closure",
    "road closure",
    "road closed",
    "closed to traffic",
    "roving",
]


async def scrape_dot_closures() -> list[RoadClosure]:
    """
    Scrape current lane closures from Hawaii DOT Maui page.

    The DOT page has no structured HTML containers per closure entry.
    We target <p> tags that contain lane/road closure keywords and
    parse road name, status, and location from the text.

    4x4 Logging: inputs (URL), outputs (closure count), timing, status
    """
    global _dot_cache, _dot_last_scraped

    start_time = time.time()
    logger.info(f"INPUT  | scrape_dot_closures | url={DOT_MAUI_URL}")

    closures = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                DOT_MAUI_URL,
                headers={"User-Agent": "MauiAlertHub/1.0"},
                follow_redirects=True,
            )
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")

        i = 0
        for p in paragraphs:
            text = p.get_text(separator=" ", strip=True)
            text_lower = text.lower()

            if not any(kw in text_lower for kw in _CLOSURE_KEYWORDS):
                continue
            if len(text) < 20:
                logger.debug(f"SKIP   | dot | too short: {text[:40]}")
                continue

            road_name = _dot_extract_road_name(text)
            if road_name == "Unknown Road":
                logger.debug(f"SKIP   | dot | no road name found: {text[:60]}")
                continue

            closure = RoadClosure(
                id=f"dot-{i}",
                road_name=road_name,
                status=_dot_determine_status(text),
                description=text[:300],
                location=_dot_extract_location(text),
                source="Hawaii DOT",
                updated_at=datetime.now(),
            )
            closures.append(closure)
            i += 1

        _dot_cache = closures
        _dot_last_scraped = datetime.now()

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | scrape_dot_closures | count={len(closures)} | "
            f"time={duration_ms:.1f}ms | OK"
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | scrape_dot_closures | error={str(e)} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )
        return _dot_cache

    return closures


def get_cached_dot_roads() -> tuple[list[RoadClosure], Optional[datetime]]:
    """Return cached DOT road data and when it was last scraped."""
    return _dot_cache, _dot_last_scraped


def _dot_extract_road_name(text: str) -> str:
    """
    Extract road name from DOT closure text.

    Real DOT formats:
      "Right merge lane closed on Puunene Avenue (Route 3500) in the southbound..."
      "Left lane closure on Honoapiilani Highway (Route 30) in the northbound..."
      "Right single lane closure on Crater Road (Route 378) the northbound..."
    """
    m = re.search(
        r'(?i)\bon\s+'
        r'([A-Z][A-Za-z\s/]+?'
        r'(?:Highway|Avenue|Road|Street|Drive|Hwy|Ave|Rd|Blvd)'
        r'(?:\s*\([^)]+\))?)'
        r'\s*(?:in\s+the|in\s+both|\bthe\b|between|,|\bat\b|$)',
        text,
    )
    if m:
        return m.group(1).strip()
    return "Unknown Road"


def _dot_determine_status(text: str) -> RoadStatus:
    """
    DOT closures are almost always partial lane closures (RESTRICTED).
    Full road closures are rare but do happen.
    """
    lower = text.lower()
    if "road closure" in lower or "road closed" in lower or "closed to traffic" in lower:
        return RoadStatus.CLOSED
    if "lane closed" in lower or "lane closure" in lower or "roving" in lower:
        return RoadStatus.RESTRICTED
    return RoadStatus.UNKNOWN


def _dot_extract_location(text: str) -> Optional[str]:
    """
    Extract the specific location from DOT closure text.

    Handles:
      "between Prison Street and Dickenson Street"
      "at Wakea Avenue"
      "between mile marker 0.4 and 0.5"
    """
    m = re.search(r'(?i)\bbetween\s+(.+?)(?:\s*,|\s+for\s|\.\s*$|$)', text)
    if m:
        return m.group(1).strip()[:100]

    m = re.search(
        r'(?i)\bat\s+([A-Z][A-Za-z\s]+?'
        r'(?:Avenue|Road|Street|Highway|Hwy|Ave|Rd|St))',
        text,
    )
    if m:
        return m.group(1).strip()[:100]

    return None
