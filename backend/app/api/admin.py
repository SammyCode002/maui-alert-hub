"""
Admin API — protected community alert management.

All routes require: Authorization: Bearer <ADMIN_TOKEN>

POST   /api/admin/alerts        — create alert
GET    /api/admin/alerts        — list all alerts (including inactive)
DELETE /api/admin/alerts/{id}   — deactivate alert
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Header, Request
from sqlalchemy import text

from app.database import engine
from app.models.schemas import CommunityAlert, CommunityAlertCreate, CommunityAlertsResponse
from app.services.config import settings
from app.services.limiter import limiter, ADMIN

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
@limiter.limit(ADMIN)
async def create_alert(
    request: Request,
    body: CommunityAlertCreate,
    authorization: str | None = Header(default=None),
):
    """Create a new community alert (power outage, water main, etc.)."""
    _require_admin(authorization)

    expires_str = body.expires_at.isoformat() if body.expires_at else None

    async with engine.connect() as conn:
        result = await conn.execute(text(
            """
            INSERT INTO community_alerts (title, message, severity, expires_at)
            VALUES (:title, :message, :severity, :expires_at)
            RETURNING id
            """
        ), {
            "title": body.title,
            "message": body.message,
            "severity": body.severity,
            "expires_at": expires_str,
        })
        alert_id = result.scalar()
        await conn.commit()

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
@limiter.limit(ADMIN)
async def list_all_alerts(
    request: Request,
    authorization: str | None = Header(default=None),
):
    """List all community alerts including inactive/expired (admin view)."""
    _require_admin(authorization)

    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT * FROM community_alerts ORDER BY created_at DESC"
        ))
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


@router.delete("/alerts/{alert_id}", status_code=200)
@limiter.limit(ADMIN)
async def deactivate_alert(
    request: Request,
    alert_id: int,
    authorization: str | None = Header(default=None),
):
    """Deactivate (soft-delete) a community alert."""
    _require_admin(authorization)

    async with engine.connect() as conn:
        result = await conn.execute(text(
            "UPDATE community_alerts SET is_active = 0 WHERE id = :id"
        ), {"id": alert_id})
        await conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert not found")

    logger.info(f"Community alert deactivated: id={alert_id}")
    return {"status": "deactivated", "id": alert_id}
