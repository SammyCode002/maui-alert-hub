"""
Data models for Maui Alert Hub.

These are Pydantic models, which serve two purposes:
1. They validate data (if a field is wrong type, you get a clear error)
2. They auto-generate the API docs at /docs

WHY Pydantic models?
Think of them like blueprints. When data comes in from a scraper or goes
out to the frontend, these models make sure it has the right shape.
No more "undefined is not a function" surprises.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# Enums (predefined choices)
# ============================================================

class RoadStatus(str, Enum):
    """Possible states a road can be in."""
    OPEN = "open"
    CLOSED = "closed"
    RESTRICTED = "restricted"  # e.g., local traffic only
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """NWS alert severity levels."""
    EXTREME = "extreme"
    SEVERE = "severe"
    MODERATE = "moderate"
    MINOR = "minor"
    UNKNOWN = "unknown"


class AlertType(str, Enum):
    """Types of weather alerts."""
    WARNING = "warning"
    WATCH = "watch"
    ADVISORY = "advisory"
    STATEMENT = "statement"


# ============================================================
# Road Models
# ============================================================

class RoadClosure(BaseModel):
    """
    Represents a single road closure or restriction on Maui.

    Example:
        {
            "road_name": "Hana Highway (360)",
            "status": "restricted",
            "description": "Twin Falls to Hana, local residents and essential workers only",
            "location": "Twin Falls to Hana",
            "source": "Maui County",
            "updated_at": "2026-03-20T10:00:00"
        }
    """
    id: Optional[str] = Field(None, description="Unique identifier")
    road_name: str = Field(..., description="Name of the road (e.g., 'Hana Highway (360)')")
    status: RoadStatus = Field(..., description="Current road status")
    description: str = Field(..., description="Details about the closure or restriction")
    location: Optional[str] = Field(None, description="Specific location on the road")
    source: str = Field(default="Maui County", description="Where this info came from")
    updated_at: datetime = Field(default_factory=datetime.now, description="When this was last updated")


class RoadResponse(BaseModel):
    """API response wrapper for road data."""
    roads: list[RoadClosure]
    total: int
    last_scraped: Optional[datetime] = None


# ============================================================
# Weather Models
# ============================================================

class WeatherAlert(BaseModel):
    """
    A weather alert from the National Weather Service.

    Example:
        {
            "headline": "Flood Watch in effect through Sunday afternoon",
            "severity": "moderate",
            "alert_type": "watch",
            "description": "Flash flooding caused by excessive rainfall is possible.",
            "areas": "Maui, Molokai, Lanai",
            "onset": "2026-03-20T06:00:00",
            "expires": "2026-03-22T18:00:00"
        }
    """
    id: Optional[str] = Field(None, description="NWS alert ID")
    headline: str = Field(..., description="Short summary of the alert")
    severity: AlertSeverity = Field(..., description="How serious is this")
    alert_type: AlertType = Field(..., description="Warning, watch, or advisory")
    description: str = Field(..., description="Full alert description")
    areas: Optional[str] = Field(None, description="Affected areas")
    onset: Optional[datetime] = Field(None, description="When the alert starts")
    expires: Optional[datetime] = Field(None, description="When the alert expires")
    source: str = Field(default="NWS", description="National Weather Service")


class WeatherForecast(BaseModel):
    """Simple weather forecast for a period (e.g., 'Tonight', 'Saturday')."""
    name: str = Field(..., description="Period name (e.g., 'Tonight', 'Saturday')")
    temperature: int = Field(..., description="Temperature in Fahrenheit")
    wind_speed: str = Field(..., description="Wind speed description")
    wind_direction: str = Field(..., description="Wind direction (e.g., 'NE')")
    short_forecast: str = Field(..., description="Brief forecast (e.g., 'Scattered Showers')")
    detailed_forecast: str = Field(..., description="Full forecast text")
    is_daytime: bool = Field(..., description="True if daytime period")


class WeatherResponse(BaseModel):
    """API response wrapper for weather data."""
    alerts: list[WeatherAlert]
    forecasts: list[WeatherForecast]
    location: str = "Maui, Hawaii"
    last_updated: Optional[datetime] = None


# ============================================================
# Earthquake Models
# ============================================================

class Earthquake(BaseModel):
    """
    A single earthquake event from the USGS Earthquake Hazards Program.

    Example:
        {
            "id": "us7000abc1",
            "magnitude": 3.5,
            "place": "5km NW of Kahului, Hawaii",
            "time": "2026-03-22T10:00:00+00:00",
            "depth_km": 8.5,
            "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us7000abc1"
        }
    """
    id: str = Field(..., description="USGS event ID")
    magnitude: float = Field(..., description="Richter magnitude")
    place: str = Field(..., description="Human-readable location description")
    time: datetime = Field(..., description="Event time (UTC)")
    depth_km: float = Field(..., description="Depth below surface in kilometers")
    url: str = Field(..., description="USGS event detail page URL")


class EarthquakeResponse(BaseModel):
    """API response wrapper for earthquake data."""
    earthquakes: list[Earthquake]
    total: int
    last_updated: Optional[datetime] = None
