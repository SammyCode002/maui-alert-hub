"""
Shared rate limiter instance for all API routes.

Uses slowapi (wraps the `limits` library) with per-IP tracking.
Import `limiter` in any router file to apply rate limit decorators.

Rate limit tiers:
  GENERAL  = 100 requests / 15 minutes  (data endpoints)
  NOTIFY   = 30  requests / 15 minutes  (subscribe / unsubscribe)
  ADMIN    = 20  requests / 15 minutes  (admin write operations)
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Named limit strings — import these instead of repeating the string literals
GENERAL = "100/15minutes"
NOTIFY  = "30/15minutes"
ADMIN   = "20/15minutes"
