"""
Pytest configuration and shared fixtures.

Ensures the SQLite database is initialized before any tests run,
so tables like alert_history, seen_alert_ids, etc. exist.
"""

import asyncio
import pytest
from app.database import init_db


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Create all DB tables before the test session starts."""
    asyncio.run(init_db())
