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


# ============================================================
# Volcanic Activity Models
# ============================================================

class VolcanicAlert(BaseModel):
    """
    A volcanic activity notification from the USGS Volcano Notification Service.

    Alert levels (ground hazards): Normal, Advisory, Watch, Warning
    Aviation colors: Green, Yellow, Orange, Red
    """
    id: str = Field(..., description="Notification ID")
    volcano_name: str = Field(..., description="Volcano name (e.g., 'Kīlauea')")
    alert_level: str = Field(..., description="Alert level: Normal/Advisory/Watch/Warning")
    aviation_color: str = Field(..., description="Aviation color code: Green/Yellow/Orange/Red")
    message: str = Field(..., description="Notification summary text")
    published: datetime = Field(..., description="Publication timestamp")
    url: str = Field(default="", description="Link to full notification")


class VolcanicResponse(BaseModel):
    """API response wrapper for volcanic activity data."""
    alerts: list[VolcanicAlert]
    total: int
    last_updated: Optional[datetime] = None


# ============================================================
# Surf Report Models
# ============================================================

class SurfSpot(BaseModel):
    """
    Current surf conditions at a NOAA NDBC buoy station.

    Wave height is converted from meters to feet.
    Water temperature is converted from Celsius to Fahrenheit.
    """
    buoy_id: str = Field(..., description="NDBC station ID")
    name: str = Field(..., description="Human-readable location name")
    wave_height_ft: Optional[float] = Field(None, description="Significant wave height in feet")
    period_sec: Optional[float] = Field(None, description="Dominant wave period in seconds")
    direction: Optional[str] = Field(None, description="Wave direction (e.g., 'NW')")
    water_temp_f: Optional[float] = Field(None, description="Sea surface temperature in Fahrenheit")
    updated_at: datetime = Field(default_factory=datetime.now)


class SurfResponse(BaseModel):
    """API response wrapper for surf data."""
    spots: list[SurfSpot]
    last_updated: Optional[datetime] = None


# ============================================================
# Push Notification Models
# ============================================================

class PushSubscriptionKeys(BaseModel):
    """Web Push subscription key material."""
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    """Incoming subscribe request body from the browser."""
    endpoint: str
    keys: PushSubscriptionKeys
    saved_routes: list[str] = Field(default_factory=list)


# ============================================================
# Community Alert Models (admin-posted)
# ============================================================

class CommunityAlert(BaseModel):
    """A manually-posted community alert (power outage, water main, etc.)."""
    id: int
    title: str
    message: str
    severity: str = "warning"
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True


class CommunityAlertCreate(BaseModel):
    """Request body for creating a community alert."""
    title: str = Field(..., min_length=3, max_length=120)
    message: str = Field(..., min_length=10, max_length=1000)
    severity: str = Field(default="warning", pattern="^(info|warning|danger)$")
    expires_at: Optional[datetime] = None


class CommunityAlertsResponse(BaseModel):
    """API response wrapper for community alerts."""
    alerts: list[CommunityAlert]
    total: int


# ============================================================
# Tsunami Models
# ============================================================

class TsunamiAlert(BaseModel):
    """
    A tsunami alert issued by NWS/PTWC for Hawaii coastal areas.

    Event types: Tsunami Warning, Tsunami Watch, Tsunami Advisory,
    Tsunami Information Statement.
    """
    id: Optional[str] = Field(None, description="NWS alert ID")
    event: str = Field(..., description="Alert event type (e.g., 'Tsunami Warning')")
    severity: AlertSeverity = Field(..., description="Alert severity")
    headline: str = Field(..., description="Short summary headline")
    description: str = Field(..., description="Full alert description")
    areas: Optional[str] = Field(None, description="Affected areas")
    onset: Optional[datetime] = Field(None, description="Alert start time")
    expires: Optional[datetime] = Field(None, description="Alert expiry time")


class TsunamiResponse(BaseModel):
    """API response wrapper for tsunami data."""
    alerts: list[TsunamiAlert]
    last_updated: Optional[datetime] = None


# ============================================================
# Air Quality Models
# ============================================================

class AQIReading(BaseModel):
    """
    A single air quality reading from EPA AirNow.

    AQI Categories:
      1 Good (0-50), 2 Moderate (51-100), 3 USG (101-150),
      4 Unhealthy (151-200), 5 Very Unhealthy (201-300), 6 Hazardous (301+)
    """
    parameter: str = Field(..., description="Pollutant name (e.g., 'PM2.5', 'O3')")
    aqi: int = Field(..., description="Air Quality Index value")
    category: str = Field(..., description="Category name (e.g., 'Good')")
    category_number: int = Field(..., description="Category number 1-6")
    reporting_area: str = Field(..., description="Monitoring area name")


class AQIResponse(BaseModel):
    """API response wrapper for air quality data."""
    readings: list[AQIReading]
    location: str = "Maui, Hawaii"
    last_updated: Optional[datetime] = None
    is_vog_advisory: bool = Field(
        default=False,
        description="True when any PM2.5 or SO2 reading is Unhealthy or worse"
    )
