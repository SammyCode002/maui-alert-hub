"""Time helpers.

Use ``utcnow()`` everywhere instead of ``datetime.now()`` so that
timestamps are timezone-aware (UTC) and serialize with a ``+00:00``
suffix. Without the suffix the browser parses the ISO string as
local time, which on a UTC-hosted server (Render) means Maui
residents see UTC clock values labeled as Hawaii time.
"""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)
