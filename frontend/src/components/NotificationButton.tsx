/**
 * Bell icon button that toggles Web Push notification subscription.
 * Only renders if push is supported and VAPID is configured on the backend.
 */

import { Bell, BellOff } from 'lucide-react'
import { useNotifications } from '../hooks/useNotifications'

export default function NotificationButton() {
  const { supported, subscribed, loading, subscribe, unsubscribe } = useNotifications()

  if (!supported) return null

  return (
    <button
      onClick={subscribed ? unsubscribe : subscribe}
      disabled={loading}
      title={subscribed ? 'Disable alerts' : 'Enable push alerts'}
      className="p-2.5 rounded-xl bg-white/[0.05] border border-white/[0.09] hover:bg-white/[0.10] transition-colors disabled:opacity-50"
      aria-label={subscribed ? 'Unsubscribe from alerts' : 'Subscribe to alerts'}
    >
      {subscribed
        ? <Bell className="w-4 h-4 text-ocean-300" />
        : <BellOff className="w-4 h-4 text-ocean-500" />
      }
    </button>
  )
}
