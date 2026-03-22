"""
NOAA National Data Buoy Center (NDBC) client for Maui surf conditions.

Fetches real-time buoy observations and parses wave height, period,
direction, and water temperature.

Buoys used:
  51101 — Pauwela, Maui (north swell indicator, Hookipa/North Shore)
  51001 — Northwest Hawaii (offshore swell, leading indicator)

NDBC realtime data format: fixed-width text, updated hourly.
Columns: YY MM DD hh mm WDIR WSPD GST WVHT DPD APD MWD PRES ATMP WTMP ...
"MM" means missing data for that field.

NDBC data: https://www.ndbc.noaa.gov/
"""

import logging
import time
from datetime import datetime
from typing import Optional

import httpx

from app.models.schemas import SurfSpot

logger = logging.getLogger("maui_alert_hub.buoy")

NDBC_BASE = "https://www.ndbc.noaa.gov/data/realtime2"

BUOYS = [
    {"id": "51101", "name": "North Maui (Pauwela)"},
    {"id": "51001", "name": "NW Hawaii (Offshore)"},
]

# In-memory cache
_surf_cache: list[SurfSpot] = []
_surf_last_fetched: Optional[datetime] = None

# Column indices (0-based) in the NDBC realtime text format
_COL_WVHT = 8   # Significant wave height (m)
_COL_DPD  = 9   # Dominant wave period (s)
_COL_MWD  = 11  # Mean wave direction (degrees)
_COL_WTMP = 14  # Sea surface temperature (C)


async def fetch_surf_conditions() -> list[SurfSpot]:
    """
    Fetch surf conditions from NOAA NDBC buoys near Maui.

    Returns cached data on error.

    4x4 Logging: inputs (buoy IDs), outputs (spot count), timing, status
    """
    global _surf_cache, _surf_last_fetched

    start_time = time.time()
    logger.info(f"INPUT  | fetch_surf_conditions | buoys={[b['id'] for b in BUOYS]}")

    spots = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for buoy in BUOYS:
            spot = await _fetch_buoy(client, buoy["id"], buoy["name"])
            if spot:
                spots.append(spot)

    if spots:
        _surf_cache = spots
        _surf_last_fetched = datetime.now()

    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        f"OUTPUT | fetch_surf_conditions | count={len(spots)} | "
        f"time={duration_ms:.1f}ms | {'OK' if spots else 'EMPTY'}"
    )

    return spots if spots else _surf_cache


def get_cached_surf() -> tuple[list[SurfSpot], Optional[datetime]]:
    """Return cached surf data and when it was last fetched."""
    return _surf_cache, _surf_last_fetched


async def _fetch_buoy(
    client: httpx.AsyncClient, buoy_id: str, name: str
) -> Optional[SurfSpot]:
    """Fetch and parse a single NDBC buoy observation."""
    url = f"{NDBC_BASE}/{buoy_id}.txt"
    try:
        response = await client.get(url, headers={"User-Agent": "MauiAlertHub/1.0"})
        response.raise_for_status()
        return _parse_buoy_text(response.text, buoy_id, name)
    except Exception as e:
        logger.warning(f"Buoy {buoy_id} fetch failed: {e}")
        return None


def _parse_buoy_text(text: str, buoy_id: str, name: str) -> Optional[SurfSpot]:
    """
    Parse NDBC fixed-width text into a SurfSpot.

    Skips header lines (start with #) and rows with MM (missing) wave height.
    Returns the most recent row with valid wave data.
    """
    lines = text.strip().splitlines()
    data_lines = [l for l in lines if not l.startswith("#")]

    for line in data_lines:
        parts = line.split()
        if len(parts) < 15:
            continue

        wvht_raw = parts[_COL_WVHT]
        if wvht_raw == "MM":
            continue  # skip rows with missing wave height

        try:
            wave_height_m = float(wvht_raw)
            wave_height_ft = round(wave_height_m * 3.28084, 1)

            period_raw = parts[_COL_DPD]
            period_sec = float(period_raw) if period_raw != "MM" else None

            mwd_raw = parts[_COL_MWD]
            direction = _degrees_to_cardinal(float(mwd_raw)) if mwd_raw != "MM" else None

            wtmp_raw = parts[_COL_WTMP]
            water_temp_f = (
                round(float(wtmp_raw) * 9 / 5 + 32, 1)
                if wtmp_raw != "MM" else None
            )

            return SurfSpot(
                buoy_id=buoy_id,
                name=name,
                wave_height_ft=wave_height_ft,
                period_sec=period_sec,
                direction=direction,
                water_temp_f=water_temp_f,
                updated_at=datetime.now(),
            )
        except (ValueError, IndexError):
            continue

    return None


def _degrees_to_cardinal(degrees: float) -> str:
    """Convert compass degrees to 16-point cardinal direction string."""
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    idx = round(degrees / 22.5) % 16
    return directions[idx]
