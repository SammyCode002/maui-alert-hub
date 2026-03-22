"""
Public community alerts endpoint — GET /api/community-alerts/

Returns active admin-posted alerts (power outages, water mains, etc.)
Anyone can read; only admins can write (see api/admin.py).
"""

import logging
from datetime import datetime

from fastapi import APIRouter

from app.database import DB_PATH
from app.models.schemas import CommunityAlertsResponse, CommunityAlert

import aiosqlite

logger = logging.getLogger("maui_alert_hub.api.community")
router = APIRouter()


@router.get("/", response_model=CommunityAlertsResponse)
async def get_community_alerts():
    """
    Get all active community alerts.

    Excludes expired alerts (expires_at in the past) and inactive ones.
    """
    now = datetime.now().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT id, title, message, severity, created_at, expires_at, is_active
            FROM community_alerts
            WHERE is_active = 1
              AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY created_at DESC
            """,
            (now,),
        )
        rows = await cursor.fetchall()

    alerts = [
        CommunityAlert(
            id=row["id"],
            title=row["title"],
            message=row["message"],
            severity=row["severity"],
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
            is_active=bool(row["is_active"]),
        )
        for row in rows
    ]

    return CommunityAlertsResponse(alerts=alerts, total=len(alerts))
