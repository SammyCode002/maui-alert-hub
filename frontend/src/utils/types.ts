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

// ============================================================
// Earthquake Types
// ============================================================

export interface Earthquake {
  id: string
  magnitude: number
  place: string
  time: string
  depth_km: number
  url: string
}

export interface EarthquakeResponse {
  earthquakes: Earthquake[]
  total: number
  last_updated: string | null
}

// ============================================================
// Volcanic Activity Types
// ============================================================

export interface VolcanicAlert {
  id: string
  volcano_name: string
  alert_level: string
  aviation_color: string
  message: string
  published: string
  url: string
}

export interface VolcanicResponse {
  alerts: VolcanicAlert[]
  total: number
  last_updated: string | null
}

// ============================================================
// Surf Types
// ============================================================

export interface SurfSpot {
  buoy_id: string
  name: string
  wave_height_ft: number | null
  period_sec: number | null
  direction: string | null
  water_temp_f: number | null
  updated_at: string
}

export interface SurfResponse {
  spots: SurfSpot[]
  last_updated: string | null
}

// ============================================================
// Community Alert Types
// ============================================================

export type AlertSeverityLevel = 'info' | 'warning' | 'danger'

export interface CommunityAlert {
  id: number
  title: string
  message: string
  severity: AlertSeverityLevel
  created_at: string
  expires_at: string | null
  is_active: boolean
}

export interface CommunityAlertsResponse {
  alerts: CommunityAlert[]
  total: number
}

// ============================================================
// Tsunami Types
// ============================================================

export interface TsunamiAlert {
  id: string | null
  event: string
  severity: AlertSeverity
  headline: string
  description: string
  areas: string | null
  onset: string | null
  expires: string | null
}

export interface TsunamiResponse {
  alerts: TsunamiAlert[]
  last_updated: string | null
}

// ============================================================
// Air Quality Types
// ============================================================

export interface AQIReading {
  parameter: string
  aqi: number
  category: string
  category_number: number
  reporting_area: string
}

export interface AQIResponse {
  readings: AQIReading[]
  location: string
  last_updated: string | null
  is_vog_advisory: boolean
}

// ============================================================
// Forecast City
// ============================================================

export type ForecastCityKey =
  | 'kahului' | 'wailuku'
  | 'makawao' | 'pukalani'
  | 'paia' | 'haiku'
  | 'lahaina' | 'kapalua'
  | 'kihei' | 'wailea'
  | 'hana'

export const FORECAST_CITIES: Record<ForecastCityKey, string> = {
  // Central
  kahului: 'Kahului',
  wailuku: 'Wailuku',
  // Upcountry
  makawao: 'Makawao',
  pukalani: 'Pukalani',
  // North Shore
  paia: 'Paia',
  haiku: 'Haiku',
  // West Maui
  lahaina: 'Lahaina',
  kapalua: 'Kapalua',
  // South Maui
  kihei: 'Kihei',
  wailea: 'Wailea',
  // East Maui
  hana: 'Hana',
}
