"""
USGS Earthquake Hazards Program API client.

Fetches recent earthquakes near Maui from the USGS free GeoJSON feed.
No API key required.

Search area: 300km radius from Kahului (covers all main Hawaiian Islands).
Minimum magnitude: 2.5 (earthquakes felt by people, not just instruments).

USGS API docs: https://earthquake.usgs.gov/fdsnws/event/1/
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.models.schemas import Earthquake

logger = logging.getLogger("maui_alert_hub.usgs")

USGS_BASE = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Maui coordinates (Kahului)
MAUI_LAT = 20.8893
MAUI_LON = -156.4729

# 300km covers Maui, Oahu, Big Island, Kauai
SEARCH_RADIUS_KM = 300
MIN_MAGNITUDE = 2.5
MAX_RESULTS = 10


async def fetch_earthquakes() -> list[Earthquake]:
    """
    Fetch recent earthquakes near Maui from the USGS GeoJSON API.

    Returns up to 10 earthquakes ordered by most recent first.
    On error, returns an empty list (non-fatal — dashboard still works).

    4x4 Logging: inputs (coordinates, radius), outputs (count), timing, status
    """
    start_time = time.time()
    logger.info(
        f"INPUT  | fetch_earthquakes | lat={MAUI_LAT} lon={MAUI_LON} "
        f"radius={SEARCH_RADIUS_KM}km minmag={MIN_MAGNITUDE}"
    )

    earthquakes = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                USGS_BASE,
                params={
                    "format": "geojson",
                    "latitude": MAUI_LAT,
                    "longitude": MAUI_LON,
                    "maxradiuskm": SEARCH_RADIUS_KM,
                    "minmagnitude": MIN_MAGNITUDE,
                    "orderby": "time",
                    "limit": MAX_RESULTS,
                },
            )
            response.raise_for_status()
            data = response.json()

        for feature in data.get("features", []):
            eq = _parse_earthquake_feature(feature)
            if eq:
                earthquakes.append(eq)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | fetch_earthquakes | count={len(earthquakes)} | "
            f"time={duration_ms:.1f}ms | OK"
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | fetch_earthquakes | error={str(e)} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )

    return earthquakes


def _parse_earthquake_feature(feature: dict) -> Optional[Earthquake]:
    """
    Parse a single USGS GeoJSON feature into an Earthquake model.

    USGS GeoJSON structure:
      feature.id                          -> event ID
      feature.properties.mag              -> magnitude (float)
      feature.properties.place            -> location string
      feature.properties.time             -> milliseconds since epoch (int)
      feature.properties.url              -> USGS event URL
      feature.geometry.coordinates[2]     -> depth in km (float)
    """
    try:
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])

        mag = props.get("mag")
        place = props.get("place", "Unknown location")
        time_ms = props.get("time")
        url = props.get("url", "")
        depth_km = coords[2] if len(coords) > 2 else 0.0

        if mag is None or time_ms is None:
            return None

        return Earthquake(
            id=feature.get("id", ""),
            magnitude=round(float(mag), 1),
            place=place,
            time=datetime.fromtimestamp(time_ms / 1000, tz=timezone.utc),
            depth_km=round(float(depth_km), 1),
            url=url,
        )
    except Exception:
        return None
