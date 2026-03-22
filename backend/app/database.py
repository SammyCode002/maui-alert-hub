"""
SQLite database setup using aiosqlite.

Tables:
  push_subscriptions  — Web Push subscriber endpoints + saved route IDs
  seen_alert_ids      — NWS alert IDs already notified about (prevents duplicates)
  seen_road_ids       — Road closure IDs already notified about
  community_alerts    — Admin-posted alerts (power outages, water mains, etc.)
  alert_history       — Past NWS alerts for the history view (last 7 days)

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
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint     TEXT    UNIQUE NOT NULL,
    p256dh       TEXT    NOT NULL,
    auth         TEXT    NOT NULL,
    saved_routes TEXT    DEFAULT '[]',
    created_at   TEXT    DEFAULT (datetime('now'))
)
"""

CREATE_SEEN_ALERT_IDS = """
CREATE TABLE IF NOT EXISTS seen_alert_ids (
    alert_id   TEXT PRIMARY KEY,
    first_seen TEXT DEFAULT (datetime('now'))
)
"""

CREATE_SEEN_ROAD_IDS = """
CREATE TABLE IF NOT EXISTS seen_road_ids (
    road_id    TEXT PRIMARY KEY,
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

CREATE_ALERT_HISTORY = """
CREATE TABLE IF NOT EXISTS alert_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nws_id       TEXT    UNIQUE,
    headline     TEXT    NOT NULL,
    severity     TEXT    NOT NULL,
    alert_type   TEXT    NOT NULL,
    areas        TEXT,
    onset        TEXT,
    expires      TEXT,
    first_seen_at TEXT   DEFAULT (datetime('now'))
)
"""


async def init_db() -> None:
    """Create all tables and run any schema migrations. Called once on startup."""
    logger.info("Initializing SQLite database")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_PUSH_SUBSCRIPTIONS)
        await db.execute(CREATE_SEEN_ALERT_IDS)
        await db.execute(CREATE_SEEN_ROAD_IDS)
        await db.execute(CREATE_COMMUNITY_ALERTS)
        await db.execute(CREATE_ALERT_HISTORY)

        # Migrate existing push_subscriptions table to add saved_routes if missing
        try:
            await db.execute(
                "ALTER TABLE push_subscriptions ADD COLUMN saved_routes TEXT DEFAULT '[]'"
            )
            logger.info("Migrated push_subscriptions: added saved_routes column")
        except Exception:
            pass  # Column already exists

        await db.commit()
    logger.info("Database ready")


async def get_db():
    """Yield an aiosqlite connection. Use as an async context manager."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
