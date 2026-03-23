"""
Public community alerts endpoint — GET /api/community-alerts/

Returns active admin-posted alerts (power outages, water mains, etc.)
Anyone can read; only admins can write (see api/admin.py).
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Request
from sqlalchemy import text

from app.database import engine
from app.models.schemas import CommunityAlertsResponse, CommunityAlert
from app.services.limiter import limiter, GENERAL

logger = logging.getLogger("maui_alert_hub.api.community")
router = APIRouter()


@router.get("/", response_model=CommunityAlertsResponse)
@limiter.limit(GENERAL)
async def get_community_alerts(request: Request):
    """
    Get all active community alerts.

    Excludes expired alerts (expires_at in the past) and inactive ones.
    """
    now = datetime.now().isoformat()

    async with engine.connect() as conn:
        result = await conn.execute(text(
            """
            SELECT id, title, message, severity, created_at, expires_at, is_active
            FROM community_alerts
            WHERE is_active = 1
              AND (expires_at IS NULL OR expires_at > :now)
            ORDER BY created_at DESC
            """
        ), {"now": now})
        rows = result.mappings().fetchall()

    alerts = [
        CommunityAlert(
            id=row["id"],
            title=row["title"],
            message=row["message"],
            severity=row["severity"],
            created_at=datetime.fromisoformat(str(row["created_at"])),
            expires_at=datetime.fromisoformat(str(row["expires_at"])) if row["expires_at"] else None,
            is_active=bool(row["is_active"]),
        )
        for row in rows
    ]

    return CommunityAlertsResponse(alerts=alerts, total=len(alerts))
