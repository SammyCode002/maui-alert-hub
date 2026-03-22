"""
SQLite database setup using aiosqlite.

Three tables:
  push_subscriptions  — Web Push subscriber endpoints (for push notifications)
  seen_alert_ids      — NWS alert IDs already notified about (prevents duplicate pushes)
  community_alerts    — Admin-posted alerts (power outages, water mains, etc.)

NOTE: On Render free tier the filesystem persists between restarts but is reset
on each new deploy. Push subscriptions will be lost after each deploy. Users will
need to re-enable notifications after an app update. This is acceptable for MVP.
For production, migrate to a hosted database (Supabase, Railway, etc.).
"""

import aiosqlite
import logging

logger = logging.getLogger("maui_alert_hub.database")

DB_PATH = "./maui_alert_hub.db"

CREATE_PUSH_SUBSCRIPTIONS = """
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT    UNIQUE NOT NULL,
    p256dh   TEXT    NOT NULL,
    auth     TEXT    NOT NULL,
    created_at TEXT  DEFAULT (datetime('now'))
)
"""

CREATE_SEEN_ALERT_IDS = """
CREATE TABLE IF NOT EXISTS seen_alert_ids (
    alert_id   TEXT PRIMARY KEY,
    first_seen TEXT DEFAULT (datetime('now'))
)
"""

CREATE_COMMUNITY_ALERTS = """
CREATE TABLE IF NOT EXISTS community_alerts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    message    TEXT    NOT NULL,
    severity   TEXT    DEFAULT 'warning',
    created_at TEXT    DEFAULT (datetime('now')),
    expires_at TEXT,
    is_active  INTEGER DEFAULT 1
)
"""


async def init_db() -> None:
    """Create all tables if they don't exist. Called once on startup."""
    logger.info("Initializing SQLite database")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_PUSH_SUBSCRIPTIONS)
        await db.execute(CREATE_SEEN_ALERT_IDS)
        await db.execute(CREATE_COMMUNITY_ALERTS)
        await db.commit()
    logger.info("Database ready")


async def get_db():
    """Yield an aiosqlite connection. Use as an async context manager."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
