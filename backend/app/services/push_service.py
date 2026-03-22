"""
Web Push notification service.

Handles:
  - Storing/removing push subscriptions
  - Detecting new NWS alerts (diff against previously seen IDs)
  - Sending push notifications to all subscribers via VAPID

VAPID keys must be set in env vars:
  VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL

If keys are not configured, push sending is silently skipped.
"""

import json
import logging
from typing import Optional

import aiosqlite
from pywebpush import webpush, WebPushException

from app.database import DB_PATH
from app.services.config import settings

logger = logging.getLogger("maui_alert_hub.push")


def _vapid_configured() -> bool:
    return bool(settings.vapid_private_key and settings.vapid_public_key)


# ============================================================
# Subscription management
# ============================================================

async def save_subscription(endpoint: str, p256dh: str, auth: str) -> None:
    """Insert or ignore a push subscription."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO push_subscriptions (endpoint, p256dh, auth) VALUES (?, ?, ?)",
            (endpoint, p256dh, auth),
        )
        await db.commit()
    logger.info(f"Subscription saved: {endpoint[:40]}...")


async def delete_subscription(endpoint: str) -> None:
    """Remove a push subscription by endpoint."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM push_subscriptions WHERE endpoint = ?", (endpoint,)
        )
        await db.commit()
    logger.info(f"Subscription removed: {endpoint[:40]}...")


async def get_all_subscriptions() -> list[dict]:
    """Return all stored push subscriptions."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT endpoint, p256dh, auth FROM push_subscriptions")
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


# ============================================================
# Alert diff — detect new NWS alerts
# ============================================================

async def get_seen_alert_ids() -> set[str]:
    """Return set of alert IDs already notified about."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT alert_id FROM seen_alert_ids")
        rows = await cursor.fetchall()
    return {row[0] for row in rows}


async def mark_alerts_seen(alert_ids: list[str]) -> None:
    """Store alert IDs so we don't notify about them again."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany(
            "INSERT OR IGNORE INTO seen_alert_ids (alert_id) VALUES (?)",
            [(aid,) for aid in alert_ids],
        )
        await db.commit()


async def check_and_notify_new_alerts(current_alerts) -> None:
    """
    Compare current NWS alerts against previously seen IDs.
    For each new alert, send a push notification to all subscribers.
    """
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
            "title": f"Maui Alert: {alert.alert_type.value.title()}",
            "body": alert.headline,
            "tag": alert.id,
            "url": "/",
        }
        await _broadcast_push(payload)

    await mark_alerts_seen(current_ids)


# ============================================================
# Send push to all subscribers
# ============================================================

async def _broadcast_push(payload: dict) -> None:
    """Send a push notification to every stored subscriber."""
    subscriptions = await get_all_subscriptions()
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
                vapid_claims={
                    "sub": settings.vapid_email,
                },
            )
        except WebPushException as e:
            logger.warning(f"Push failed for {sub['endpoint'][:40]}: {e}")
            # 410 Gone = subscription expired/revoked, remove it
            if hasattr(e, "response") and e.response and e.response.status_code == 410:
                failed_endpoints.append(sub["endpoint"])
        except Exception as e:
            logger.error(f"Unexpected push error: {e}")

    # Clean up expired subscriptions
    for endpoint in failed_endpoints:
        await delete_subscription(endpoint)
