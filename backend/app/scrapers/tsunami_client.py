"""
Tsunami alert client for Maui Alert Hub.

Fetches active tsunami alerts from the NWS API, filtered for Hawaii.
The Pacific Tsunami Warning Center (PTWC) issues products through NWS,
so querying NWS with area=HI captures all active tsunami alerts.

Tsunami event types:
  - Tsunami Warning     (most severe — evacuate now)
  - Tsunami Watch       (possible threat, be ready)
  - Tsunami Advisory    (strong currents, stay off shore)
  - Tsunami Information Statement (no threat, informational)
"""

import logging
import time
from typing import Optional

import httpx

from app.models.schemas import AlertSeverity, TsunamiAlert, TsunamiResponse
from app.services.config import settings

logger = logging.getLogger("maui_alert_hub.tsunami")

NWS_BASE = "https://api.weather.gov"

# Tsunami-specific NWS event types (case-sensitive match on "tsunami")
TSUNAMI_EVENT_KEYWORDS = {"tsunami warning", "tsunami watch", "tsunami advisory", "tsunami information"}

# In-memory cache
_tsunami_cache: Optional[TsunamiResponse] = None
_tsunami_last_fetched: float = 0.0
_CACHE_TTL_SECONDS = 120  # 2 minutes — tsunamis need near-realtime data


def _get_headers() -> dict:
    return {
        "User-Agent": settings.nws_user_agent,
        "Accept": "application/geo+json",
    }


def _is_tsunami_event(event: str) -> bool:
    """Return True if the NWS event name is tsunami-related."""
    return "tsunami" in event.lower()


def _map_severity(nws_severity: str) -> AlertSeverity:
    mapping = {
        "Extreme": AlertSeverity.EXTREME,
        "Severe": AlertSeverity.SEVERE,
        "Moderate": AlertSeverity.MODERATE,
        "Minor": AlertSeverity.MINOR,
    }
    return mapping.get(nws_severity, AlertSeverity.UNKNOWN)


async def fetch_tsunami_alerts() -> TsunamiResponse:
    """
    Fetch active tsunami alerts for Hawaii from NWS.

    Queries the NWS alerts API for the entire state of Hawaii (area=HI)
    and filters for tsunami event types.

    4x4 Logging: inputs (area), outputs (alert count), timing, status
    """
    global _tsunami_cache, _tsunami_last_fetched

    start_time = time.time()
    logger.info("INPUT  | fetch_tsunami_alerts | area=HI")

    # Serve from cache if fresh
    if _tsunami_cache is not None and (time.time() - _tsunami_last_fetched) < _CACHE_TTL_SECONDS:
        logger.info(f"OUTPUT | fetch_tsunami_alerts | cached | count={len(_tsunami_cache.alerts)}")
        return _tsunami_cache

    alerts: list[TsunamiAlert] = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NWS_BASE}/alerts/active",
                params={"area": "HI"},
                headers=_get_headers(),
            )
            response.raise_for_status()
            data = response.json()

        for feature in data.get("features", []):
            props = feature.get("properties", {})
            event = props.get("event", "")

            if not _is_tsunami_event(event):
                continue

            alerts.append(TsunamiAlert(
                id=props.get("id"),
                event=event,
                severity=_map_severity(props.get("severity", "")),
                headline=props.get("headline", event),
                description=props.get("description", ""),
                areas=props.get("areaDesc"),
                onset=props.get("onset"),
                expires=props.get("expires"),
            ))

        result = TsunamiResponse(alerts=alerts)
        _tsunami_cache = result
        _tsunami_last_fetched = time.time()

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | fetch_tsunami_alerts | count={len(alerts)} | "
            f"time={duration_ms:.1f}ms | OK"
        )
        return result

    except httpx.HTTPError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | fetch_tsunami_alerts | error={e} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )
        if _tsunami_cache is not None:
            return _tsunami_cache
        return TsunamiResponse(alerts=[])
