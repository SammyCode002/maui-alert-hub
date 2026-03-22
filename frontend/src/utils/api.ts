/**
 * API client for Maui Alert Hub backend.
 *
 * WHY a separate API file?
 * Keeps all fetch logic in one place. If the API URL changes or you need
 * to add auth headers later, you update ONE file instead of every component.
 */

import type { RoadResponse, WeatherResponse } from './types'

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

export async function getWeather(): Promise<WeatherResponse> {
  return fetchAPI<WeatherResponse>('/weather/')
}

export async function getWeatherAlerts() {
  return fetchAPI('/weather/alerts')
}

export async function getWeatherForecast() {
  return fetchAPI('/weather/forecast')
}
