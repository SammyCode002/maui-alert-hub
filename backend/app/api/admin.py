"""
Admin API — protected community alert management.

All routes require: Authorization: Bearer <ADMIN_TOKEN>

POST   /api/admin/alerts        — create alert
GET    /api/admin/alerts        — list all alerts (including inactive)
DELETE /api/admin/alerts/{id}   — deactivate alert
"""

import logging
from datetime import datetime

import aiosqlite
from fastapi import APIRouter, HTTPException, Header

from app.database import DB_PATH
from app.models.schemas import CommunityAlert, CommunityAlertCreate, CommunityAlertsResponse
from app.services.config import settings

logger = logging.getLogger("maui_alert_hub.api.admin")
router = APIRouter()


def _require_admin(authorization: str | None) -> None:
    """Raise 401 if Authorization header is missing or token is wrong."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization[len("Bearer "):]
    if token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")


@router.post("/alerts", response_model=CommunityAlert, status_code=201)
async def create_alert(
    body: CommunityAlertCreate,
    authorization: str | None = Header(default=None),
):
    """Create a new community alert (power outage, water main, etc.)."""
    _require_admin(authorization)

    expires_str = body.expires_at.isoformat() if body.expires_at else None

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO community_alerts (title, message, severity, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (body.title, body.message, body.severity, expires_str),
        )
        await db.commit()
        alert_id = cursor.lastrowid

    logger.info(f"Community alert created: id={alert_id} title={body.title!r}")

    return CommunityAlert(
        id=alert_id,
        title=body.title,
        message=body.message,
        severity=body.severity,
        created_at=datetime.now(),
        expires_at=body.expires_at,
        is_active=True,
    )


@router.get("/alerts", response_model=CommunityAlertsResponse)
async def list_all_alerts(
    authorization: str | None = Header(default=None),
):
    """List all community alerts including inactive/expired (admin view)."""
    _require_admin(authorization)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM community_alerts ORDER BY created_at DESC"
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


@router.delete("/alerts/{alert_id}", status_code=200)
async def deactivate_alert(
    alert_id: int,
    authorization: str | None = Header(default=None),
):
    """Deactivate (soft-delete) a community alert."""
    _require_admin(authorization)

    async with aiosqlite.connect(DB_PATH) as db:
        result = await db.execute(
            "UPDATE community_alerts SET is_active = 0 WHERE id = ?", (alert_id,)
        )
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found")

    logger.info(f"Community alert deactivated: id={alert_id}")
    return {"status": "deactivated", "id": alert_id}
