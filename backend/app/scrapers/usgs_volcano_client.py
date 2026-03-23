"""
USGS Volcano client.

Fetches currently elevated Hawaii volcanoes from the USGS HANS public API.

Endpoint: GET /hans-public/api/volcano/getElevatedVolcanoes
Returns volcanoes where alert level >= Advisory or color code >= Yellow.
HVO (Hawaiian Volcano Observatory) volcanoes are filtered to keep results
relevant to Hawaii residents.

Alert levels (ground hazards): Normal -> Advisory -> Watch -> Warning
Aviation color codes:           Green  -> Yellow   -> Orange -> Red

API docs: https://volcanoes.usgs.gov/hans-public/api/volcano/
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.models.schemas import VolcanicAlert

logger = logging.getLogger("maui_alert_hub.volcano")

USGS_ELEVATED_URL = "https://volcanoes.usgs.gov/hans-public/api/volcano/getElevatedVolcanoes"

# In-memory cache
_volcano_cache: list[VolcanicAlert] = []
_volcano_last_fetched: Optional[datetime] = None


async def fetch_volcanic_alerts() -> list[VolcanicAlert]:
    """
    Fetch currently elevated Hawaii volcano alerts from USGS HANS API.

    Returns cached data on error. Filters to HVO-monitored volcanoes.

    4x4 Logging: inputs (URL), outputs (alert count), timing, status
    """
    global _volcano_cache, _volcano_last_fetched

    start_time = time.time()
    logger.info(f"INPUT  | fetch_volcanic_alerts | url={USGS_ELEVATED_URL}")

    alerts = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                USGS_ELEVATED_URL,
                headers={"User-Agent": "MauiAlertHub/1.0"},
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()

        for item in data if isinstance(data, list) else []:
            alert = _parse_elevated_volcano(item)
            if alert:
                alerts.append(alert)

        _volcano_cache = alerts
        _volcano_last_fetched = datetime.now()

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | fetch_volcanic_alerts | count={len(alerts)} | "
            f"time={duration_ms:.1f}ms | OK"
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | fetch_volcanic_alerts | error={str(e)} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )
        return _volcano_cache

    return alerts


def get_cached_volcanic_alerts() -> tuple[list[VolcanicAlert], Optional[datetime]]:
    """Return cached volcanic alert data and when it was last fetched."""
    return _volcano_cache, _volcano_last_fetched


def _parse_elevated_volcano(item: dict) -> Optional[VolcanicAlert]:
    """
    Parse one USGS HANS elevated-volcano record into a VolcanicAlert.

    Response fields:
      obs_abbr, obs_fullname, volcano_name, vnum,
      notice_type_cd, notice_identifier, sent_utc, sent_unixtime,
      color_code, alert_level, notice_url, notice_data
    """
    try:
        # Only include HVO-monitored volcanoes (Hawaii)
        if item.get("obs_abbr", "").upper() != "HVO":
            return None

        name = item.get("volcano_name", "").strip()
        if not name:
            return None

        alert_level = item.get("alert_level") or "Advisory"
        aviation_color = item.get("color_code") or "Yellow"

        notice_type = (item.get("notice_type_cd") or "").replace("_", " ").title()
        message = (
            f"{notice_type} — Alert Level: {alert_level}, "
            f"Aviation Color: {aviation_color}"
        )

        # sent_unixtime is seconds since epoch
        unix_ts = item.get("sent_unixtime")
        if unix_ts:
            published = datetime.fromtimestamp(int(unix_ts), tz=timezone.utc)
        else:
            sent_utc = item.get("sent_utc", "")
            published = _parse_date(sent_utc)

        notif_id = str(item.get("notice_identifier") or f"{name}-{published.timestamp()}")
        url = item.get("notice_url") or ""

        return VolcanicAlert(
            id=notif_id,
            volcano_name=name,
            alert_level=alert_level,
            aviation_color=aviation_color,
            message=message,
            published=published,
            url=url,
        )
    except Exception:
        return None


def _parse_date(raw) -> datetime:
    """Parse a date string into a datetime. Falls back to now."""
    if not raw:
        return datetime.now(tz=timezone.utc)
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except Exception:
        return datetime.now(tz=timezone.utc)
