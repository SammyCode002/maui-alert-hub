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

# Maui cities for multi-city forecast
# lat/lon used to look up NWS grid points dynamically
MAUI_CITIES: dict[str, dict] = {
    # Central Maui
    "kahului":  {"lat": 20.8893, "lon": -156.4729, "label": "Kahului"},
    "wailuku":  {"lat": 20.8900, "lon": -156.5027, "label": "Wailuku"},
    # Upcountry
    "makawao":  {"lat": 20.8547, "lon": -156.3014, "label": "Makawao"},
    "pukalani": {"lat": 20.8292, "lon": -156.3367, "label": "Pukalani"},
    # North Shore
    "paia":     {"lat": 20.9117, "lon": -156.3692, "label": "Paia"},
    "haiku":    {"lat": 20.9183, "lon": -156.3097, "label": "Haiku"},
    # West Maui
    "lahaina":  {"lat": 20.8783, "lon": -156.6825, "label": "Lahaina"},
    "kapalua":  {"lat": 21.0050, "lon": -156.6671, "label": "Kapalua"},
    # South Maui
    "kihei":    {"lat": 20.7644, "lon": -156.4450, "label": "Kihei"},
    "wailea":   {"lat": 20.6803, "lon": -156.4415, "label": "Wailea"},
    # East Maui
    "hana":     {"lat": 20.7579, "lon": -155.9892, "label": "Hana"},
}

# Pre-seed Kahului grid so startup doesn't need an extra API call
_city_grid_cache: dict[str, dict] = {
    "kahului": {"office": "HFO", "x": 212, "y": 126},
}


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


async def _resolve_city_grid(city_key: str) -> Optional[dict]:
    """
    Look up the NWS grid point for a Maui city by querying /points/{lat},{lon}.
    Result is cached so we only query once per city per process lifetime.

    4x4 Logging: inputs (city/coords), outputs (grid), timing, status
    """
    if city_key in _city_grid_cache:
        return _city_grid_cache[city_key]

    city = MAUI_CITIES.get(city_key)
    if not city:
        logger.warning(f"INPUT  | _resolve_city_grid | unknown city={city_key}")
        return None

    start_time = time.time()
    logger.info(f"INPUT  | _resolve_city_grid | city={city_key} lat={city['lat']} lon={city['lon']}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NWS_BASE}/points/{city['lat']},{city['lon']}",
                headers=_get_headers(),
            )
            response.raise_for_status()
            data = response.json()

        props = data.get("properties", {})
        grid = {
            "office": props.get("gridId", MAUI_GRID_OFFICE),
            "x": props.get("gridX", MAUI_GRID_X),
            "y": props.get("gridY", MAUI_GRID_Y),
        }
        _city_grid_cache[city_key] = grid

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | _resolve_city_grid | city={city_key} "
            f"grid={grid['office']}/{grid['x']},{grid['y']} | "
            f"time={duration_ms:.1f}ms | OK"
        )
        return grid

    except httpx.HTTPError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | _resolve_city_grid | city={city_key} error={e} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )
        return None


async def fetch_forecast_for_city(city_key: str = "kahului") -> list[WeatherForecast]:
    """
    Fetch the 7-day NWS forecast for a specific Maui city.

    Falls back to Kahului forecast if the city grid can't be resolved.

    4x4 Logging: inputs (city), outputs (period count), timing, status
    """
    city_key = city_key.lower().strip()
    if city_key not in MAUI_CITIES:
        city_key = "kahului"

    start_time = time.time()
    logger.info(f"INPUT  | fetch_forecast_for_city | city={city_key}")

    grid = await _resolve_city_grid(city_key)
    if not grid:
        logger.warning(f"fetch_forecast_for_city | fallback to Kahului for city={city_key}")
        return await fetch_forecast()

    forecasts: list[WeatherForecast] = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{NWS_BASE}/gridpoints/{grid['office']}/{grid['x']},{grid['y']}/forecast",
                headers=_get_headers(),
            )
            response.raise_for_status()
            data = response.json()

        for period in data.get("properties", {}).get("periods", []):
            forecasts.append(WeatherForecast(
                name=period.get("name", ""),
                temperature=period.get("temperature", 0),
                wind_speed=period.get("windSpeed", ""),
                wind_direction=period.get("windDirection", ""),
                short_forecast=period.get("shortForecast", ""),
                detailed_forecast=period.get("detailedForecast", ""),
                is_daytime=period.get("isDaytime", True),
            ))

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"OUTPUT | fetch_forecast_for_city | city={city_key} "
            f"periods={len(forecasts)} | time={duration_ms:.1f}ms | OK"
        )

    except httpx.HTTPError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"OUTPUT | fetch_forecast_for_city | city={city_key} error={e} | "
            f"time={duration_ms:.1f}ms | ERROR"
        )
        return await fetch_forecast()

    return forecasts
