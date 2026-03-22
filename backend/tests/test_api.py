"""
Tests for the Maui Alert Hub API.

Run with: pytest tests/ -v

WHY test?
Even a simple health check test catches import errors, missing dependencies,
and broken routes before your users do. Start simple, add more as you build.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /api/health endpoint."""

    def test_health_returns_200(self):
        """Health check should always return 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self):
        """Health check should report 'healthy' status."""
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_includes_version(self):
        """Health check should include the app version."""
        response = client.get("/api/health")
        data = response.json()
        assert "version" in data

    def test_health_includes_timestamp(self):
        """Health check should include a timestamp."""
        response = client.get("/api/health")
        data = response.json()
        assert "timestamp" in data


class TestRootEndpoint:
    """Tests for the / root endpoint."""

    def test_root_returns_200(self):
        """Root should return 200 with app info."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_includes_app_name(self):
        """Root should identify the app."""
        response = client.get("/")
        data = response.json()
        assert data["app"] == "Maui Alert Hub API"

    def test_root_includes_docs_link(self):
        """Root should point to the API docs."""
        response = client.get("/")
        data = response.json()
        assert data["docs"] == "/docs"


class TestRoadsEndpoint:
    """Tests for the /api/roads/ endpoint."""

    def test_roads_returns_200(self):
        """Roads endpoint should return 200 even with no data."""
        response = client.get("/api/roads/")
        assert response.status_code == 200

    def test_roads_returns_expected_shape(self):
        """Roads response should have roads list, total, and last_scraped."""
        response = client.get("/api/roads/")
        data = response.json()
        assert "roads" in data
        assert "total" in data
        assert isinstance(data["roads"], list)


class TestWeatherEndpoint:
    """Tests for the /api/weather/ endpoint.

    NOTE: These tests hit the real NWS API. In a production test suite,
    you'd mock the API calls. For MVP, real calls are fine since NWS
    is free and reliable.
    """

    def test_weather_returns_200(self):
        """Weather endpoint should return 200."""
        response = client.get("/api/weather/")
        assert response.status_code == 200

    def test_weather_returns_expected_shape(self):
        """Weather response should have alerts and forecasts."""
        response = client.get("/api/weather/")
        data = response.json()
        assert "alerts" in data
        assert "forecasts" in data
        assert "location" in data


class TestModels:
    """Tests for Pydantic data models."""

    def test_road_closure_model(self):
        """RoadClosure model should accept valid data."""
        from app.models.schemas import RoadClosure, RoadStatus

        road = RoadClosure(
            id="test-1",
            road_name="Hana Highway",
            status=RoadStatus.CLOSED,
            description="Closed due to flooding at Twin Falls",
            location="Twin Falls",
            source="Maui County",
        )
        assert road.road_name == "Hana Highway"
        assert road.status == RoadStatus.CLOSED

    def test_weather_alert_model(self):
        """WeatherAlert model should accept valid data."""
        from app.models.schemas import WeatherAlert, AlertSeverity, AlertType

        alert = WeatherAlert(
            headline="Flood Watch in effect",
            severity=AlertSeverity.MODERATE,
            alert_type=AlertType.WATCH,
            description="Flash flooding possible due to heavy rain.",
            areas="Maui",
        )
        assert alert.severity == AlertSeverity.MODERATE
        assert alert.alert_type == AlertType.WATCH
