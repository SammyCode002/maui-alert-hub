/**
 * Shared TypeScript types for Maui Alert Hub.
 *
 * These mirror the Pydantic models on the backend so the frontend
 * and backend always agree on data shapes.
 */

// ============================================================
// Road Types
// ============================================================

export type RoadStatus = 'open' | 'closed' | 'restricted' | 'unknown'

export interface RoadClosure {
  id: string | null
  road_name: string
  status: RoadStatus
  description: string
  location: string | null
  source: string
  updated_at: string
}

export interface RoadResponse {
  roads: RoadClosure[]
  total: number
  last_scraped: string | null
}

// ============================================================
// Weather Types
// ============================================================

export type AlertSeverity = 'extreme' | 'severe' | 'moderate' | 'minor' | 'unknown'
export type AlertType = 'warning' | 'watch' | 'advisory' | 'statement'

export interface WeatherAlert {
  id: string | null
  headline: string
  severity: AlertSeverity
  alert_type: AlertType
  description: string
  areas: string | null
  onset: string | null
  expires: string | null
  source: string
}

export interface WeatherForecast {
  name: string
  temperature: number
  wind_speed: string
  wind_direction: string
  short_forecast: string
  detailed_forecast: string
  is_daytime: boolean
}

export interface WeatherResponse {
  alerts: WeatherAlert[]
  forecasts: WeatherForecast[]
  location: string
  last_updated: string | null
}
