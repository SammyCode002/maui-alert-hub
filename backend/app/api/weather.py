"""
Weather API endpoints.

GET /api/weather/                    - Alerts + forecast (Kahului default)
GET /api/weather/alerts              - Active weather alerts only
GET /api/weather/forecast?city=kihei - 7-day forecast for a specific Maui city

Supported city values: kahului, lahaina, kihei, hana, paia, wailea
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Query

from app.models.schemas import WeatherResponse
from app.scrapers.nws_client import (
    MAUI_CITIES,
    fetch_alerts,
    fetch_forecast,
    fetch_forecast_for_city,
)
from app.services.push_service import check_and_notify_new_alerts

logger = logging.getLogger("maui_alert_hub.api.weather")

router = APIRouter()


@router.get("/", response_model=WeatherResponse)
async def get_weather(
    city: str = Query(default="kahului", description="Maui city for forecast"),
):
    """
    Get the full weather picture for Maui: active alerts + 7-day forecast.

    Pass ?city=kihei (or lahaina, hana, paia, wailea) to get a
    location-specific forecast. Alerts always cover all of Maui County.
    """
    city_key = city.lower().strip()
    if city_key not in MAUI_CITIES:
        city_key = "kahului"

    alerts, forecasts = await _fetch_weather(city_key)

    city_label = MAUI_CITIES[city_key]["label"]
    return WeatherResponse(
        alerts=alerts,
        forecasts=forecasts,
        location=f"{city_label}, Maui",
        last_updated=datetime.now(),
    )


async def _fetch_weather(city_key: str):
    """Helper: fetch alerts + forecast concurrently, trigger push check."""
    import asyncio
    alerts, forecasts = await asyncio.gather(
        fetch_alerts(),
        fetch_forecast_for_city(city_key),
    )
    await check_and_notify_new_alerts(alerts)
    return alerts, forecasts


@router.get("/alerts")
async def get_weather_alerts():
    """Get only active weather alerts for Maui County."""
    alerts = await fetch_alerts()
    return {
        "alerts": alerts,
        "total": len(alerts),
        "last_updated": datetime.now().isoformat(),
    }


@router.get("/forecast")
async def get_weather_forecast(
    city: str = Query(default="kahului", description="Maui city for forecast"),
):
    """
    Get the 7-day NWS forecast for a specific Maui city.

    Supported values: kahului, lahaina, kihei, hana, paia, wailea
    """
    city_key = city.lower().strip()
    if city_key not in MAUI_CITIES:
        city_key = "kahului"

    forecasts = await fetch_forecast_for_city(city_key)
    city_label = MAUI_CITIES[city_key]["label"]

    return {
        "forecasts": forecasts,
        "total": len(forecasts),
        "location": f"{city_label}, Maui",
        "city": city_key,
        "available_cities": {k: v["label"] for k, v in MAUI_CITIES.items()},
        "last_updated": datetime.now().isoformat(),
    }
