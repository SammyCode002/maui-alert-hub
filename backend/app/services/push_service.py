"""
Web Push notification service.

Handles:
  - Storing/removing push subscriptions (with saved route IDs per subscriber)
  - Detecting new NWS weather alerts and broadcasting to all subscribers
  - Detecting new road closures and notifying only subscribers who saved that road
  - Recording alert history for the dashboard history view

VAPID keys must be set in env vars:
  VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL

If keys are not configured, push sending is silently skipped.
"""

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import text
from pywebpush import webpush, WebPushException

from app.database import engine
from app.services.config import settings

logger = logging.getLogger("maui_alert_hub.push")


def _vapid_configured() -> bool:
    return bool(settings.vapid_private_key and settings.vapid_public_key)


# ============================================================
# Subscription management
# ============================================================

async def save_subscription(endpoint: str, p256dh: str, auth: str, saved_routes: list[str] | None = None) -> None:
    """Insert or update a push subscription with optional saved road IDs."""
    routes_json = json.dumps(saved_routes or [])
    async with engine.connect() as conn:
        await conn.execute(text(
            """INSERT INTO push_subscriptions (endpoint, p256dh, auth, saved_routes)
               VALUES (:endpoint, :p256dh, :auth, :saved_routes)
               ON CONFLICT(endpoint) DO UPDATE SET
                 p256dh=excluded.p256dh,
                 auth=excluded.auth,
                 saved_routes=excluded.saved_routes"""
        ), {"endpoint": endpoint, "p256dh": p256dh, "auth": auth, "saved_routes": routes_json})
        await conn.commit()
    logger.info(f"Subscription saved: {endpoint[:40]}... routes={len(saved_routes or [])}")


async def update_subscription_routes(endpoint: str, saved_routes: list[str]) -> None:
    """Update the saved road IDs for an existing subscription."""
    async with engine.connect() as conn:
        await conn.execute(text(
            "UPDATE push_subscriptions SET saved_routes = :saved_routes WHERE endpoint = :endpoint"
        ), {"saved_routes": json.dumps(saved_routes), "endpoint": endpoint})
        await conn.commit()
    logger.info(f"Updated saved routes for {endpoint[:40]}... count={len(saved_routes)}")


async def delete_subscription(endpoint: str) -> None:
    """Remove a push subscription by endpoint."""
    async with engine.connect() as conn:
        await conn.execute(text(
            "DELETE FROM push_subscriptions WHERE endpoint = :endpoint"
        ), {"endpoint": endpoint})
        await conn.commit()
    logger.info(f"Subscription removed: {endpoint[:40]}...")


async def get_all_subscriptions() -> list[dict]:
    """Return all stored push subscriptions including saved_routes."""
    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT endpoint, p256dh, auth, saved_routes FROM push_subscriptions"
        ))
        rows = result.mappings().fetchall()
    output = []
    for row in rows:
        d = dict(row)
        try:
            d["saved_routes"] = json.loads(d.get("saved_routes") or "[]")
        except Exception:
            d["saved_routes"] = []
        output.append(d)
    return output


# ============================================================
# Alert history
# ============================================================

async def record_alert_history(alerts) -> None:
    """Upsert current NWS alerts into alert_history table."""
    async with engine.connect() as conn:
        for alert in alerts:
            if not alert.id:
                continue
            await conn.execute(text(
                """INSERT INTO alert_history
                   (nws_id, headline, severity, alert_type, areas, onset, expires)
                   VALUES (:nws_id, :headline, :severity, :alert_type, :areas, :onset, :expires)
                   ON CONFLICT(nws_id) DO NOTHING"""
            ), {
                "nws_id": alert.id,
                "headline": alert.headline,
                "severity": alert.severity.value,
                "alert_type": alert.alert_type.value,
                "areas": alert.areas,
                "onset": alert.onset.isoformat() if alert.onset else None,
                "expires": alert.expires.isoformat() if alert.expires else None,
            })
        await conn.commit()


async def get_alert_history(days: int = 7) -> list[dict]:
    """Return alert history for the last N days, newest first."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    async with engine.connect() as conn:
        result = await conn.execute(text(
            """SELECT * FROM alert_history
               WHERE first_seen_at >= :cutoff
               ORDER BY first_seen_at DESC"""
        ), {"cutoff": cutoff})
        rows = result.mappings().fetchall()
    return [dict(row) for row in rows]


# ============================================================
# NWS alert diff — detect new alerts, broadcast to all
# ============================================================

async def get_seen_alert_ids() -> set[str]:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT alert_id FROM seen_alert_ids"))
        rows = result.fetchall()
    return {row[0] for row in rows}


async def mark_alerts_seen(alert_ids: list[str]) -> None:
    async with engine.connect() as conn:
        await conn.execute(text(
            "INSERT INTO seen_alert_ids (alert_id) VALUES (:alert_id) ON CONFLICT DO NOTHING"
        ), [{"alert_id": aid} for aid in alert_ids])
        await conn.commit()


async def check_and_notify_new_alerts(current_alerts) -> None:
    """
    Compare current NWS alerts against previously seen IDs.
    Broadcasts new alerts to ALL subscribers (weather alerts are always relevant).
    Also records all alerts in history.
    """
    await record_alert_history(current_alerts)

    if not _vapid_configured():
        return

    current_ids = [a.id for a in current_alerts if a.id]
    if not current_ids:
        return

    seen = await get_seen_alert_ids()
    new_alerts = [a for a in current_alerts if a.id and a.id not in seen]

    if not new_alerts:
        await mark_alerts_seen(current_ids)
        return

    logger.info(f"New NWS alerts detected: {len(new_alerts)}")
    for alert in new_alerts:
        payload = {
            "title": f"Maui {alert.alert_type.value.title()}",
            "body": alert.headline,
            "tag": alert.id,
            "url": "/#alerts",
        }
        await _broadcast_push(payload)

    await mark_alerts_seen(current_ids)


# ============================================================
# Road closure diff — notify only subscribers with saved routes
# ============================================================

async def get_seen_road_ids() -> set[str]:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT road_id FROM seen_road_ids"))
        rows = result.fetchall()
    return {row[0] for row in rows}


async def mark_roads_seen(road_ids: list[str]) -> None:
    async with engine.connect() as conn:
        await conn.execute(text(
            "INSERT INTO seen_road_ids (road_id) VALUES (:road_id) ON CONFLICT DO NOTHING"
        ), [{"road_id": rid} for rid in road_ids])
        await conn.commit()


async def check_and_notify_road_closures(current_roads) -> None:
    """
    Compare current road closures against previously seen IDs.
    For each NEW closure, notify only subscribers who have that road saved.
    """
    if not _vapid_configured():
        return

    road_ids = [r.id for r in current_roads if r.id]
    if not road_ids:
        return

    seen = await get_seen_road_ids()
    new_roads = [r for r in current_roads if r.id and r.id not in seen]

    if not new_roads:
        await mark_roads_seen(road_ids)
        return

    logger.info(f"New road closures detected: {len(new_roads)}")
    subscriptions = await get_all_subscriptions()

    for road in new_roads:
        interested = [
            sub for sub in subscriptions
            if road.id in sub.get("saved_routes", [])
        ]
        if not interested:
            logger.debug(f"No subscribers have {road.road_name} saved, skipping push")
            continue

        payload = {
            "title": f"Road Update: {road.road_name}",
            "body": f"{road.status.value.title()} — {road.description[:100]}",
            "tag": f"road-{road.id}",
            "url": "/#roads",
        }
        await _send_push_to(payload, interested)

    await mark_roads_seen(road_ids)


# ============================================================
# Push sending helpers
# ============================================================

async def _broadcast_push(payload: dict) -> None:
    """Send a push notification to every stored subscriber."""
    subscriptions = await get_all_subscriptions()
    await _send_push_to(payload, subscriptions)


async def _send_push_to(payload: dict, subscriptions: list[dict]) -> None:
    """Send a push notification to a specific list of subscribers."""
    if not subscriptions:
        return

    failed_endpoints = []
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub["endpoint"],
                    "keys": {"p256dh": sub["p256dh"], "auth": sub["auth"]},
                },
                data=json.dumps(payload),
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_email},
            )
        except WebPushException as e:
            logger.warning(f"Push failed for {sub['endpoint'][:40]}: {e}")
            if hasattr(e, "response") and e.response and e.response.status_code == 410:
                failed_endpoints.append(sub["endpoint"])
        except Exception as e:
            logger.error(f"Unexpected push error: {e}")

    for endpoint in failed_endpoints:
        await delete_subscription(endpoint)
