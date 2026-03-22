"""
National Weather Service (NWS) API client for Maui.

The NWS API is FREE and requires NO API key. You just need to send a
User-Agent header with your app name and contact email. That's it.

HOW IT WORKS:
1. NWS organizes weather by "grid points" (lat/lon mapped to forecast offices)
2. Maui is covered by the Honolulu forecast office (HFO)
3. We hit two endpoints:
   - /alerts: Active warnings, watches, advisories
   - /gridpoints: Detailed forecasts for a specific location

NWS API Docs: https://www.weather.gov/documentation/services-web-api
"""

import logging
import time
from typing import Optional

import httpx

from app.models.schemas import (
    AlertSeverity,
    AlertType,
    WeatherAlert,
    WeatherForecast,
)
from app.services.config import settings

logger = logging.getLogger("maui_alert_hub.nws")

# NWS API base URL
NWS_BASE = "https://api.weather.gov"

# Maui grid point (Kahului area, central Maui)
# You find this by hitting: https://api.weather.gov/points/20.8893,-156.4729
MAUI_GRID_OFFICE = "HFO"  # Honolulu Forecast Office
MAUI_GRID_X = 212
MAUI_GRID_Y = 126

# Maui County zone for alerts
MAUI_ZONE = "HIZ023"  # Maui Central Valley North
MAUI_COUNTY_ZONES = ["HIZ023", "HIZ024", "HIZ025", "HIZ026"]


def _get_headers() -> dict:
    """
    Build request headers for NWS API.
    NWS requires a descriptive User-Agent string.
    """
    return {
        "User-Agent": settings.nws_user_agent,
        "Accept": "application/geo+json",
    }


async def fetch_alerts() -> list[WeatherAlert]:
    """
    Fetch active weather alerts for Maui County from NWS.

    Returns a list of WeatherAlert objects, sorted by severity (worst first).

    4x4 Logging: inputs (zone), outputs (alert count), timing, status
    """
    start_time = time.time()
    logger.info(f"INPUT  | fetch_alerts | zones={MAUI_COUNTY_ZONES}")

    alerts = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Fetch alerts for all Maui zones
            response = await client.get(
                f"{NWS_BASE}/alerts/active",
                params={"zone": ",".join(MAUI_COUNTY_ZONES)},
                headers=_get_headers(),
            )
            response.raise_for_status()
            data = response.json()

        # Parse each alert feature
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            alert = WeatherAlert(
                id=props.get("id"),
                headline=props.get("headline", "Unknown Alert"),
                severity=_map_severity(props.get("severity", "")),
                alert_type=_map_alert_type(props.get("event", "")),
                description=props.get("description", ""),
                areas=props.get("areaDesc", ""),
                onset=props.get("onset"),
                expires=props.get("expires"),
            )
            alerts.append(alert)

        # Sort: extreme first, minor last
        severity_order = {
            AlertSeverity.EXTREME: 0,
            AlertSeverity.SEVERE: 1,
            AlertSeverity.MODERATE: 2,
            AlertSeverity.MINOR: 3,
            AlertSeverity.UNKNOWN: 4,
        }
        alerts.sort(key=lambda a: severity_order.get(a.severity, 4))

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | fetch_alerts | count={len(alerts)} | "
            f"time={duration_ms:.1f}ms | OK"
        )

    except httpx.HTTPError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | fetch_alerts | error={str(e)} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )

    return alerts


async def fetch_forecast() -> list[WeatherForecast]:
    """
    Fetch the 7-day forecast for central Maui from NWS.

    Returns a list of WeatherForecast objects (one per period, e.g., "Tonight").

    4x4 Logging: inputs (grid point), outputs (period count), timing, status
    """
    start_time = time.time()
    logger.info(
        f"INPUT  | fetch_forecast | office={MAUI_GRID_OFFICE} "
        f"grid=({MAUI_GRID_X},{MAUI_GRID_Y})"
    )

    forecasts = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NWS_BASE}/gridpoints/{MAUI_GRID_OFFICE}/{MAUI_GRID_X},{MAUI_GRID_Y}/forecast",
                headers=_get_headers(),
            )
            response.raise_for_status()
            data = response.json()

        for period in data.get("properties", {}).get("periods", []):
            forecast = WeatherForecast(
                name=period.get("name", ""),
                temperature=period.get("temperature", 0),
                wind_speed=period.get("windSpeed", ""),
                wind_direction=period.get("windDirection", ""),
                short_forecast=period.get("shortForecast", ""),
                detailed_forecast=period.get("detailedForecast", ""),
                is_daytime=period.get("isDaytime", True),
            )
            forecasts.append(forecast)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | fetch_forecast | periods={len(forecasts)} | "
            f"time={duration_ms:.1f}ms | OK"
        )

    except httpx.HTTPError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | fetch_forecast | error={str(e)} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )

    return forecasts


def _map_severity(nws_severity: str) -> AlertSeverity:
    """Map NWS severity string to our enum."""
    mapping = {
        "Extreme": AlertSeverity.EXTREME,
        "Severe": AlertSeverity.SEVERE,
        "Moderate": AlertSeverity.MODERATE,
        "Minor": AlertSeverity.MINOR,
    }
    return mapping.get(nws_severity, AlertSeverity.UNKNOWN)


def _map_alert_type(event: str) -> AlertType:
    """Map NWS event name to our alert type enum."""
    event_lower = event.lower()
    if "warning" in event_lower:
        return AlertType.WARNING
    elif "watch" in event_lower:
        return AlertType.WATCH
    elif "advisory" in event_lower:
        return AlertType.ADVISORY
    return AlertType.STATEMENT
