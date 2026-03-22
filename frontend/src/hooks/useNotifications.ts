/**
 * Web Push notification hook.
 *
 * Manages the full subscription lifecycle:
 *   1. Check if push is supported and VAPID is configured
 *   2. Request notification permission
 *   3. Subscribe via pushManager (uses VITE_VAPID_PUBLIC_KEY)
 *   4. POST subscription to backend
 *   5. Track subscribed state in localStorage
 *
 * Gracefully no-ops if push is unsupported or VAPID not configured.
 */

import { useState, useEffect } from 'react'
import { getVapidPublicKey, subscribeToNotifications, unsubscribeFromNotifications } from '../utils/api'

const SUBSCRIBED_KEY = 'push-subscribed'

function urlBase64ToUint8Array(base64String: string): Uint8Array<ArrayBuffer> {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  const output = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i++) output[i] = raw.charCodeAt(i)
  return output
}

export function useNotifications() {
  const [supported, setSupported] = useState(false)
  const [subscribed, setSubscribed] = useState(
    () => localStorage.getItem(SUBSCRIBED_KEY) === 'true'
  )
  const [loading, setLoading] = useState(false)
  const [vapidKey, setVapidKey] = useState<string | null>(null)

  useEffect(() => {
    const pushSupported =
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window

    if (!pushSupported) return

    // Fetch VAPID public key from backend (fails silently if not configured)
    getVapidPublicKey().then(key => {
      if (key) {
        setVapidKey(key)
        setSupported(true)
      }
    })
  }, [])

  const subscribe = async () => {
    if (!supported || !vapidKey) return
    setLoading(true)
    try {
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') return

      const registration = await navigator.serviceWorker.ready
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidKey),
      })

      await subscribeToNotifications(subscription)
      setSubscribed(true)
      localStorage.setItem(SUBSCRIBED_KEY, 'true')
    } catch (err) {
      console.error('[Push] Subscribe failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const unsubscribe = async () => {
    setLoading(true)
    try {
      const registration = await navigator.serviceWorker.ready
      const subscription = await registration.pushManager.getSubscription()
      if (subscription) {
        await unsubscribeFromNotifications(subscription.endpoint)
        await subscription.unsubscribe()
      }
      setSubscribed(false)
      localStorage.removeItem(SUBSCRIBED_KEY)
    } catch (err) {
      console.error('[Push] Unsubscribe failed:', err)
    } finally {
      setLoading(false)
    }
  }

  return { supported, subscribed, loading, subscribe, unsubscribe }
}
