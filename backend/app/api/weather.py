"""
Weather API endpoints.

GET /api/weather/          - Get alerts + forecast for Maui
GET /api/weather/alerts    - Get only active weather alerts
GET /api/weather/forecast  - Get only the forecast
"""

import logging
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import WeatherResponse
from app.scrapers.nws_client import fetch_alerts, fetch_forecast

logger = logging.getLogger("maui_alert_hub.api.weather")

router = APIRouter()


@router.get("/", response_model=WeatherResponse)
async def get_weather():
    """
    Get the full weather picture for Maui: active alerts + 7-day forecast.

    This hits the NWS API in real-time (it's fast and free).
    """
    alerts = await fetch_alerts()
    forecasts = await fetch_forecast()

    return WeatherResponse(
        alerts=alerts,
        forecasts=forecasts,
        location="Maui, Hawaii",
        last_updated=datetime.now(),
    )


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
async def get_weather_forecast():
    """Get the 7-day forecast for central Maui."""
    forecasts = await fetch_forecast()
    return {
        "forecasts": forecasts,
        "total": len(forecasts),
        "location": "Kahului, Maui",
        "last_updated": datetime.now().isoformat(),
    }
