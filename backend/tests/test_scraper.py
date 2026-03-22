"""
Unit tests for the road closure scraper parsing logic (county + DOT).

These test the three helper functions directly — no HTTP calls needed.
This matters because the county website HTML structure can change anytime,
and these functions are the most likely place things will break.

Run with: pytest tests/test_scraper.py -v
"""

import pytest
from app.scrapers.road_scraper import (
    _is_valid_closure,
    _extract_road_name,
    _extract_location,
    _determine_status,
)
from app.scrapers.dot_scraper import (
    _dot_extract_road_name,
    _dot_determine_status,
    _dot_extract_location,
)


class TestIsValidClosure:
    """Tests for _is_valid_closure — filters nav links from real closures."""

    def test_rejects_road_closure_notifications(self):
        assert _is_valid_closure("Road Closure Notifications") is False

    def test_rejects_road_closure_notifications_double_space(self):
        assert _is_valid_closure("Road Closure  Notifications") is False

    def test_rejects_subscribe_link(self):
        assert _is_valid_closure("Subscribe to Road Closure Notifications") is False

    def test_rejects_generic_mention_of_road_closures(self):
        assert _is_valid_closure(
            "Shelter in Central Maui reopening after recent flooding, road closures"
        ) is False

    def test_accepts_road_closure_colon_format(self):
        assert _is_valid_closure("Road Closure: Lono Ave / W Kamehameha Ave") is True

    def test_accepts_allcaps_for_on_format(self):
        assert _is_valid_closure(
            "ROAD CLOSURE: 03/22/26 AT 8:19 AM FOR KAMEHAMEHA V HIGHWAY ON MOLOKA'I"
        ) is True

    def test_accepts_update_format(self):
        assert _is_valid_closure("**UPDATE LOWER KULA ROAD ** 03/22/26 AT 6:12 AM **") is True

    def test_accepts_update_format_no_date(self):
        assert _is_valid_closure("**UPDATE HALEAKALA CRATER ROAD**") is True


class TestExtractRoadName:
    """Tests for _extract_road_name — pulls the road name from alert text."""

    def test_road_closure_colon_simple(self):
        assert _extract_road_name("Road Closure: Lono Ave / W Kamehameha Ave") == "Lono Ave / W Kamehameha Ave"

    def test_road_closure_colon_with_in(self):
        assert _extract_road_name("Road Closure: Liloa St/N Laalo St in Lahaina") == "Liloa St/N Laalo St"

    def test_road_closure_colon_with_between(self):
        assert _extract_road_name(
            "Road Closure: Kuihelani Hwy between Maui Lani Pkwy to Honoapiilani Hwy"
        ) == "Kuihelani Hwy"

    def test_allcaps_for_on_format(self):
        result = _extract_road_name(
            "ROAD CLOSURE: 03/22/26 AT 8:19 AM FOR KAMEHAMEHA V HIGHWAY ON MOLOKA'I"
        )
        assert result == "Kamehameha V Highway"

    def test_update_format_with_date(self):
        assert _extract_road_name("**UPDATE LOWER KULA ROAD ** 03/22/26 AT 6:12 AM **") == "Lower Kula Road"

    def test_update_format_no_date(self):
        assert _extract_road_name("**UPDATE HALEAKALA CRATER ROAD**") == "Haleakala Crater Road"

    def test_unknown_format_returns_unknown(self):
        assert _extract_road_name("Road Closure Notifications") == "Unknown Road"

    def test_another_road_closure_colon(self):
        assert _extract_road_name("Road Closure: Puunene Ave / E Wakea Ave") == "Puunene Ave / E Wakea Ave"


class TestExtractLocation:
    """Tests for _extract_location — pulls the specific location from alert text."""

    def test_for_on_format_returns_island(self):
        result = _extract_location(
            "ROAD CLOSURE: 03/22/26 AT 8:19 AM FOR KAMEHAMEHA V HIGHWAY ON MOLOKA'I"
        )
        assert result is not None
        assert "Moloka" in result

    def test_road_closure_in_format(self):
        assert _extract_location("Road Closure: Liloa St/N Laalo St in Lahaina") == "Lahaina"

    def test_road_closure_between_format(self):
        result = _extract_location(
            "Road Closure: Kuihelani Hwy between Maui Lani Pkwy to Honoapiilani Hwy"
        )
        assert result == "Maui Lani Pkwy to Honoapiilani Hwy"

    def test_no_location_returns_none(self):
        assert _extract_location("Road Closure: Lono Ave / W Kamehameha Ave") is None

    def test_no_location_for_puunene(self):
        assert _extract_location("Road Closure: Puunene Ave / E Wakea Ave") is None

    def test_update_format_returns_none(self):
        assert _extract_location("**UPDATE LOWER KULA ROAD ** 03/22/26 AT 6:12 AM **") is None


class TestDetermineStatus:
    """Tests for _determine_status — classifies road status from text."""

    def test_closure_keyword_returns_closed(self):
        from app.models.schemas import RoadStatus
        assert _determine_status("Road Closure: Lono Ave") == RoadStatus.CLOSED

    def test_closed_keyword_returns_closed(self):
        from app.models.schemas import RoadStatus
        assert _determine_status("ROAD CLOSED due to flooding") == RoadStatus.CLOSED

    def test_update_no_closure_returns_unknown(self):
        from app.models.schemas import RoadStatus
        assert _determine_status("**UPDATE LOWER KULA ROAD **") == RoadStatus.UNKNOWN

    def test_local_only_returns_restricted(self):
        from app.models.schemas import RoadStatus
        assert _determine_status("Local traffic only on Hana Highway") == RoadStatus.RESTRICTED

    def test_open_returns_open(self):
        from app.models.schemas import RoadStatus
        assert _determine_status("Road is now open") == RoadStatus.OPEN


# ============================================================
# DOT Scraper Tests
# ============================================================

class TestDotExtractRoadName:
    """Tests for _dot_extract_road_name — parses DOT lane closure text."""

    def test_lane_closed_on_avenue_with_route(self):
        result = _dot_extract_road_name(
            "Right merge lane closed on Puunene Avenue (Route 3500) in the southbound direction at Wakea Avenue"
        )
        assert result == "Puunene Avenue (Route 3500)"

    def test_lane_closure_on_highway_with_route(self):
        result = _dot_extract_road_name(
            "Left lane closure on Honoapiilani Highway (Route 30) in the northbound direction between Prison Street and Dickenson Street"
        )
        assert result == "Honoapiilani Highway (Route 30)"

    def test_single_lane_closure_on_road(self):
        result = _dot_extract_road_name(
            "Right single lane closure on Crater Road (Route 378) the northbound direction"
        )
        assert result == "Crater Road (Route 378)"

    def test_roving_closures_on_avenue(self):
        result = _dot_extract_road_name(
            "Roving single lane closures on Puunene Avenue (Route 3500) in both directions between Wakea Avenue and Kuihelani Highway"
        )
        assert result == "Puunene Avenue (Route 3500)"

    def test_no_road_returns_unknown(self):
        assert _dot_extract_road_name("Lane closure in effect tonight") == "Unknown Road"


class TestDotDetermineStatus:
    """Tests for _dot_determine_status."""

    def test_lane_closed_returns_restricted(self):
        from app.models.schemas import RoadStatus
        assert _dot_determine_status(
            "Right merge lane closed on Puunene Avenue"
        ) == RoadStatus.RESTRICTED

    def test_lane_closure_returns_restricted(self):
        from app.models.schemas import RoadStatus
        assert _dot_determine_status(
            "Left lane closure on Honoapiilani Highway"
        ) == RoadStatus.RESTRICTED

    def test_roving_returns_restricted(self):
        from app.models.schemas import RoadStatus
        assert _dot_determine_status(
            "Roving single lane closures on Puunene Avenue"
        ) == RoadStatus.RESTRICTED

    def test_road_closure_returns_closed(self):
        from app.models.schemas import RoadStatus
        assert _dot_determine_status(
            "Road closure on Hana Highway due to rockfall"
        ) == RoadStatus.CLOSED

    def test_closed_to_traffic_returns_closed(self):
        from app.models.schemas import RoadStatus
        assert _dot_determine_status(
            "Road closed to traffic on Piilani Highway"
        ) == RoadStatus.CLOSED


class TestDotExtractLocation:
    """Tests for _dot_extract_location."""

    def test_between_cross_streets(self):
        result = _dot_extract_location(
            "Left lane closure on Honoapiilani Highway (Route 30) in the northbound direction between Prison Street and Dickenson Street, 24-hours a day"
        )
        assert result == "Prison Street and Dickenson Street"

    def test_between_mile_markers(self):
        result = _dot_extract_location(
            "Right merge lane closed on Puunene Avenue (Route 3500) at Wakea Avenue, between mile marker 0.4 and 0.5"
        )
        assert "0.4" in result

    def test_at_cross_street(self):
        result = _dot_extract_location(
            "Right merge lane closed on Puunene Avenue (Route 3500) at Wakea Avenue"
        )
        assert result == "Wakea Avenue"

    def test_no_location_returns_none(self):
        result = _dot_extract_location(
            "Lane closure on Crater Road for emergency repair work"
        )
        assert result is None
