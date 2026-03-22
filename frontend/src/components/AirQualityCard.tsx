/**
 * Displays current AQI readings for Maui with color-coded severity.
 *
 * AQI color scale:
 *   1 Good (0-50)         = green
 *   2 Moderate (51-100)   = yellow
 *   3 USG (101-150)       = orange
 *   4 Unhealthy (151-200) = red
 *   5 Very Unhealthy      = purple
 *   6 Hazardous           = maroon
 *
 * Shows a vog advisory banner when PM2.5 or SO2 is elevated.
 */

import type { AQIResponse } from '../utils/types'
import { timeAgo } from '../utils/time'

interface AirQualityCardProps {
  data: AQIResponse
}

const categoryColors: Record<number, { text: string; bg: string; bar: string }> = {
  1: { text: 'text-green-400',  bg: 'bg-green-500/20',  bar: '#22c55e' },
  2: { text: 'text-yellow-400', bg: 'bg-yellow-500/20', bar: '#eab308' },
  3: { text: 'text-orange-400', bg: 'bg-orange-500/20', bar: '#f97316' },
  4: { text: 'text-red-400',    bg: 'bg-red-500/20',    bar: '#ef4444' },
  5: { text: 'text-purple-400', bg: 'bg-purple-500/20', bar: '#a855f7' },
  6: { text: 'text-rose-300',   bg: 'bg-rose-900/40',   bar: '#881337' },
}

function getColors(categoryNumber: number) {
  return categoryColors[categoryNumber] ?? categoryColors[1]
}

function aqiBarWidth(aqi: number): string {
  // Scale 0-300 to 0-100%
  return `${Math.min(100, Math.round((aqi / 300) * 100))}%`
}

export default function AirQualityCard({ data }: AirQualityCardProps) {
  if (data.readings.length === 0) return null

  return (
    <div className="card space-y-3">
      {/* Vog advisory banner */}
      {data.is_vog_advisory && (
        <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl px-3 py-2">
          <p className="text-orange-300 text-xs font-semibold">
            Vog advisory in effect. Limit outdoor activity, especially for sensitive groups.
          </p>
        </div>
      )}

      {/* AQI readings */}
      <div className="space-y-3">
        {data.readings.map((reading) => {
          const colors = getColors(reading.category_number)
          return (
            <div key={reading.parameter}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-white text-sm font-medium">{reading.parameter}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${colors.bg} ${colors.text}`}>
                    {reading.category}
                  </span>
                </div>
                <span className={`font-display font-bold text-lg ${colors.text}`}>
                  {reading.aqi}
                </span>
              </div>
              {/* AQI bar */}
              <div className="h-1.5 bg-white/[0.07] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{ width: aqiBarWidth(reading.aqi), backgroundColor: colors.bar }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex items-center justify-between text-ocean-600 text-xs pt-1 border-t border-white/[0.06]">
        <span>{data.readings[0]?.reporting_area ?? 'Maui'}</span>
        {data.last_updated && <span>{timeAgo(data.last_updated)}</span>}
      </div>
    </div>
  )
}
