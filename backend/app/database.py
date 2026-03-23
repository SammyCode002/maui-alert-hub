"""
Database setup supporting SQLite (local dev) and PostgreSQL (production).

Set DATABASE_URL env var to a PostgreSQL connection string to use PostgreSQL.
Without it, falls back to a local SQLite file.

Accepted URL formats (auto-promoted to the async driver variant):
  (none / local dev)             -> sqlite+aiosqlite:///./maui_alert_hub.db
  postgresql://user:pass@host/db -> postgresql+asyncpg://...
  postgres://user:pass@host/db   -> Neon / Render shorthand, normalized

Tables:
  push_subscriptions  - Web Push subscriber endpoints + saved route IDs
  seen_alert_ids      - NWS alert IDs already notified (dedup)
  seen_road_ids       - Road closure IDs already notified (dedup)
  community_alerts    - Admin-posted alerts (power outages, water mains, etc.)
  alert_history       - Past NWS alerts for the history view (7 days)
"""

import logging
import os

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, MetaData, String, Table, func, text,
)
from sqlalchemy.ext.asyncio import create_async_engine

logger = logging.getLogger("maui_alert_hub.database")

# ============================================================
# URL resolution
# ============================================================

DB_PATH = "./maui_alert_hub.db"  # SQLite fallback path

_raw_url = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

if _raw_url.startswith("postgres://"):
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgresql://") and "+asyncpg" not in _raw_url:
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("sqlite://") and "+aiosqlite" not in _raw_url:
    DATABASE_URL = _raw_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
else:
    DATABASE_URL = _raw_url

IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# ============================================================
# Async engine
# ============================================================

engine = create_async_engine(DATABASE_URL, echo=False)

# ============================================================
# Table definitions (SQLAlchemy generates correct DDL per backend)
# ============================================================

metadata = MetaData()

push_subscriptions = Table(
    "push_subscriptions", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("endpoint", String, unique=True, nullable=False),
    Column("p256dh", String, nullable=False),
    Column("auth", String, nullable=False),
    Column("saved_routes", String, server_default="[]"),
    Column("created_at", DateTime, server_default=func.now()),
)

seen_alert_ids = Table(
    "seen_alert_ids", metadata,
    Column("alert_id", String, primary_key=True),
    Column("first_seen", DateTime, server_default=func.now()),
)

seen_road_ids = Table(
    "seen_road_ids", metadata,
    Column("road_id", String, primary_key=True),
    Column("first_seen", DateTime, server_default=func.now()),
)

community_alerts_table = Table(
    "community_alerts", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String, nullable=False),
    Column("message", String, nullable=False),
    Column("severity", String, server_default="warning"),
    Column("created_at", DateTime, server_default=func.now()),
    Column("expires_at", DateTime, nullable=True),
    Column("is_active", Integer, server_default="1"),
)

alert_history_table = Table(
    "alert_history", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nws_id", String, unique=True, nullable=True),
    Column("headline", String, nullable=False),
    Column("severity", String, nullable=False),
    Column("alert_type", String, nullable=False),
    Column("areas", String, nullable=True),
    Column("onset", String, nullable=True),
    Column("expires", String, nullable=True),
    Column("first_seen_at", DateTime, server_default=func.now()),
)

# ============================================================
# Lifecycle
# ============================================================

async def init_db() -> None:
    """Create all tables and run schema migrations. Called once on startup."""
    logger.info(f"Initializing database ({'PostgreSQL' if IS_POSTGRES else 'SQLite'})")

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

        # Migrate: add saved_routes to existing push_subscriptions tables
        if IS_POSTGRES:
            await conn.execute(text(
                "ALTER TABLE push_subscriptions "
                "ADD COLUMN IF NOT EXISTS saved_routes TEXT DEFAULT '[]'"
            ))
        else:
            try:
                await conn.execute(text(
                    "ALTER TABLE push_subscriptions "
                    "ADD COLUMN saved_routes TEXT DEFAULT '[]'"
                ))
                logger.info("Migrated push_subscriptions: added saved_routes column")
            except Exception:
                pass  # Column already exists

    logger.info("Database ready")


async def get_db():
    """Yield an async SQLAlchemy connection. Use as an async context manager."""
    async with engine.connect() as conn:
        yield conn
