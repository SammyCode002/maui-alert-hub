"""
Unit tests for the road closure scraper parsing logic.

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
