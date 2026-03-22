/**
 * Custom Service Worker for Maui Alert Hub.
 *
 * Handles:
 *   - Precaching of all static assets (injected by vite-plugin-pwa)
 *   - NetworkFirst runtime caching for all API endpoints
 *   - Web Push notification display
 *   - Notification click → open the app
 */

import { cleanupOutdatedCaches, precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst } from 'workbox-strategies'
import { ExpirationPlugin } from 'workbox-expiration'
import { CacheableResponsePlugin } from 'workbox-cacheable-response'

declare let self: ServiceWorkerGlobalScope

// Precache all assets built by Vite (manifest injected by vite-plugin-pwa)
cleanupOutdatedCaches()
precacheAndRoute(self.__WB_MANIFEST)

// NetworkFirst for all API calls — works for both dev proxy and prod Render URL
registerRoute(
  ({ url }) =>
    url.pathname.startsWith('/api/') ||
    url.hostname.includes('maui-alert-hub-api.onrender.com'),
  new NetworkFirst({
    cacheName: 'api-cache',
    networkTimeoutSeconds: 10,
    plugins: [
      new ExpirationPlugin({ maxEntries: 40, maxAgeSeconds: 600 }),
      new CacheableResponsePlugin({ statuses: [0, 200] }),
    ],
  })
)

// ============================================================
// Push Notifications
// ============================================================

self.addEventListener('push', (event) => {
  if (!event.data) return

  const data = event.data.json()

  event.waitUntil(
    self.registration.showNotification(data.title ?? 'Maui Alert Hub', {
      body: data.body ?? 'New alert for Maui',
      icon: '/icon.svg',
      badge: '/icon.svg',
      tag: data.tag ?? 'maui-alert',
      requireInteraction: false,
      data: { url: data.url ?? '/' },
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification.data?.url ?? '/'

  event.waitUntil(
    self.clients
      .matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            return client.focus()
          }
        }
        return self.clients.openWindow(url)
      })
  )
})
