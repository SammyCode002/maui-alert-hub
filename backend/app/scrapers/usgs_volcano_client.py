"""
USGS Volcano Notification Service client.

Fetches current alert levels and recent notifications for Hawaii volcanoes
from the USGS Volcano Notification Service (VNS) JSON feed.

Hawaii volcanoes monitored:
  - Kīlauea     (most active, Big Island)
  - Mauna Loa   (second most active, Big Island)
  - Haleakalā   (Maui — relevant to our users)
  - Hualālai    (Big Island)
  - Mauna Kea   (Big Island)

Alert levels (ground hazards): Normal → Advisory → Watch → Warning
Aviation color codes:           Green  → Yellow   → Orange → Red

USGS VNS: https://volcanoes.usgs.gov/vns2/
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.models.schemas import VolcanicAlert

logger = logging.getLogger("maui_alert_hub.volcano")

USGS_VNS_URL = "https://volcanoes.usgs.gov/vns2/notif_data/vns_notifs.json"

# In-memory cache
_volcano_cache: list[VolcanicAlert] = []
_volcano_last_fetched: Optional[datetime] = None

HAWAII_VOLCANOES = {
    "kilauea", "kīlauea",
    "mauna loa",
    "haleakala", "haleakalā",
    "hualalai", "hualālai",
    "mauna kea",
    "lo'ihi", "loihi", "lō'ihi",
}


async def fetch_volcanic_alerts() -> list[VolcanicAlert]:
    """
    Fetch current volcanic activity notifications for Hawaii volcanoes.

    Returns cached data on error. Filters to Hawaii volcanoes only.

    4x4 Logging: inputs (URL), outputs (alert count), timing, status
    """
    global _volcano_cache, _volcano_last_fetched

    start_time = time.time()
    logger.info(f"INPUT  | fetch_volcanic_alerts | url={USGS_VNS_URL}")

    alerts = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                USGS_VNS_URL,
                headers={"User-Agent": "MauiAlertHub/1.0"},
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()

        for item in data if isinstance(data, list) else []:
            alert = _parse_volcanic_notification(item)
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


def _parse_volcanic_notification(item: dict) -> Optional[VolcanicAlert]:
    """
    Parse one USGS VNS notification object into a VolcanicAlert.

    The VNS JSON uses nested objects for volcano metadata.
    Handles both flat and nested formats defensively.
    """
    try:
        # Volcano name — may be nested under "volcano" key
        volcano = item.get("volcano", {})
        name = (
            volcano.get("vName")
            or item.get("volcano_name")
            or item.get("vName")
            or ""
        )

        if not name or name.lower() not in HAWAII_VOLCANOES:
            return None

        alert_level = (
            item.get("volcanicAlertLevel")
            or item.get("alert_level")
            or "Normal"
        )
        aviation_color = (
            item.get("aviationColorCode")
            or item.get("aviation_color")
            or "Green"
        )

        # Notification text
        message = (
            item.get("notifText")
            or item.get("notification_text")
            or item.get("message")
            or "No details available."
        )
        message = str(message)[:400]

        # Publication date — try ISO string or Unix timestamp
        pub_raw = item.get("pubDate") or item.get("published_date") or item.get("pub_date")
        published = _parse_date(pub_raw)

        notif_id = str(
            item.get("notificationId")
            or item.get("id")
            or f"{name}-{published.timestamp()}"
        )

        url = item.get("archUrl") or item.get("url") or ""

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
    """Parse a date string or timestamp into a datetime. Falls back to now."""
    if raw is None:
        return datetime.now(tz=timezone.utc)
    try:
        if isinstance(raw, (int, float)):
            return datetime.fromtimestamp(raw / 1000, tz=timezone.utc)
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except Exception:
        return datetime.now(tz=timezone.utc)
