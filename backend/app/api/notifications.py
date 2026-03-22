"""
Push notification subscription endpoints.

POST /api/notifications/subscribe   — register a browser push subscription
DELETE /api/notifications/unsubscribe — remove a subscription
GET  /api/notifications/vapid-public-key — return public key for frontend
"""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import PushSubscriptionCreate
from app.services.config import settings
from app.services.push_service import save_subscription, delete_subscription, update_subscription_routes

logger = logging.getLogger("maui_alert_hub.api.notifications")
router = APIRouter()


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """Return the VAPID public key so the frontend can subscribe."""
    if not settings.vapid_public_key:
        raise HTTPException(status_code=503, detail="Push notifications not configured")
    return {"public_key": settings.vapid_public_key}


@router.post("/subscribe", status_code=201)
async def subscribe(body: PushSubscriptionCreate):
    """
    Register a browser push subscription.

    The browser sends this after calling pushManager.subscribe().
    We store the endpoint + keys so we can push alerts later.
    """
    if not settings.vapid_public_key:
        raise HTTPException(status_code=503, detail="Push notifications not configured")

    await save_subscription(
        endpoint=body.endpoint,
        p256dh=body.keys.p256dh,
        auth=body.keys.auth,
        saved_routes=body.saved_routes,
    )
    return {"status": "subscribed"}


@router.patch("/saved-routes")
async def patch_saved_routes(body: dict):
    """Update saved road IDs for an existing push subscription."""
    endpoint = body.get("endpoint")
    saved_routes = body.get("saved_routes", [])
    if not endpoint:
        raise HTTPException(status_code=400, detail="endpoint required")
    if not isinstance(saved_routes, list):
        raise HTTPException(status_code=400, detail="saved_routes must be a list")
    await update_subscription_routes(endpoint, saved_routes)
    return {"status": "updated", "count": len(saved_routes)}


@router.delete("/unsubscribe")
async def unsubscribe(body: dict):
    """Remove a push subscription by endpoint URL."""
    endpoint = body.get("endpoint")
    if not endpoint:
        raise HTTPException(status_code=400, detail="endpoint required")
    await delete_subscription(endpoint)
    return {"status": "unsubscribed"}
