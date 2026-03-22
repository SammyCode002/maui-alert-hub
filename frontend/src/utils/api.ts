/**
 * API client for Maui Alert Hub backend.
 *
 * WHY a separate API file?
 * Keeps all fetch logic in one place. If the API URL changes or you need
 * to add auth headers later, you update ONE file instead of every component.
 */

import type {
  RoadResponse, WeatherResponse, EarthquakeResponse,
  VolcanicResponse, SurfResponse, CommunityAlertsResponse,
  TsunamiResponse, AQIResponse, ForecastCityKey,
} from './types'

// In dev, Vite proxies /api to localhost:8000 (see vite.config.ts)
// In prod, this would be your actual API URL
const API_BASE = import.meta.env.VITE_API_URL || ''

/**
 * Generic fetch wrapper with error handling and 4x4 logging.
 */
async function fetchAPI<T>(endpoint: string): Promise<T> {
  const url = `${API_BASE}/api${endpoint}`
  const startTime = performance.now()

  console.log(`[API] INPUT | GET ${url}`)

  try {
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    const duration = (performance.now() - startTime).toFixed(1)

    console.log(`[API] OUTPUT | GET ${url} | status=200 | time=${duration}ms | OK`)

    return data as T
  } catch (error) {
    const duration = (performance.now() - startTime).toFixed(1)
    console.error(`[API] OUTPUT | GET ${url} | error=${error} | time=${duration}ms | ERROR`)
    throw error
  }
}

// ============================================================
// API Functions
// ============================================================

export async function getRoadClosures(): Promise<RoadResponse> {
  return fetchAPI<RoadResponse>('/roads/')
}

export async function refreshRoadClosures(): Promise<RoadResponse> {
  return fetchAPI<RoadResponse>('/roads/refresh')
}

export async function getWeather(city: ForecastCityKey = 'kahului'): Promise<WeatherResponse> {
  return fetchAPI<WeatherResponse>(`/weather/?city=${city}`)
}

export async function getWeatherAlerts() {
  return fetchAPI('/weather/alerts')
}

export async function getWeatherForecast() {
  return fetchAPI('/weather/forecast')
}

export async function getEarthquakes(): Promise<EarthquakeResponse> {
  return fetchAPI<EarthquakeResponse>('/earthquakes/')
}

export async function getVolcanic(): Promise<VolcanicResponse> {
  return fetchAPI<VolcanicResponse>('/volcanic/')
}

export async function getSurf(): Promise<SurfResponse> {
  return fetchAPI<SurfResponse>('/surf/')
}

export async function getCommunityAlerts(): Promise<CommunityAlertsResponse> {
  return fetchAPI<CommunityAlertsResponse>('/community-alerts/')
}

export async function getTsunami(): Promise<TsunamiResponse> {
  return fetchAPI<TsunamiResponse>('/tsunami/')
}

export async function getAQI(): Promise<AQIResponse> {
  return fetchAPI<AQIResponse>('/aqi/')
}

export async function getForecastForCity(city: ForecastCityKey): Promise<WeatherResponse> {
  return fetchAPI<WeatherResponse>(`/weather/?city=${city}`)
}

export async function getVapidPublicKey(): Promise<string | null> {
  try {
    const data = await fetchAPI<{ public_key: string }>('/notifications/vapid-public-key')
    return data.public_key
  } catch {
    return null
  }
}

export async function subscribeToNotifications(subscription: PushSubscription): Promise<void> {
  const sub = subscription.toJSON()
  await fetch(`${API_BASE}/api/notifications/subscribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      endpoint: sub.endpoint,
      keys: { p256dh: sub.keys?.p256dh, auth: sub.keys?.auth },
    }),
  })
}

export async function unsubscribeFromNotifications(endpoint: string): Promise<void> {
  await fetch(`${API_BASE}/api/notifications/unsubscribe`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ endpoint }),
  })
}

// Admin API
export async function adminGetAlerts(token: string) {
  const res = await fetch(`${API_BASE}/api/admin/alerts`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (res.status === 401) throw new Error('Unauthorized')
  return res.json()
}

export async function adminCreateAlert(token: string, alert: {
  title: string; message: string; severity: string; expires_at?: string | null
}) {
  const res = await fetch(`${API_BASE}/api/admin/alerts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(alert),
  })
  if (res.status === 401) throw new Error('Unauthorized')
  if (!res.ok) throw new Error('Failed to create alert')
  return res.json()
}

export async function adminDeleteAlert(token: string, id: number) {
  const res = await fetch(`${API_BASE}/api/admin/alerts/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (res.status === 401) throw new Error('Unauthorized')
  return res.json()
}
