/**
 * Horizontal scrollable forecast bar showing upcoming weather periods.
 */

import { Sun, Moon, CloudRain, Cloud } from 'lucide-react'
import type { WeatherForecast } from '../utils/types'

interface ForecastBarProps {
  forecasts: WeatherForecast[]
}

/**
 * Pick an icon based on the forecast text.
 * This is a simple keyword match, not perfect, but good enough for MVP.
 */
function getForecastIcon(forecast: string, isDaytime: boolean) {
  const lower = forecast.toLowerCase()
  if (lower.includes('rain') || lower.includes('shower') || lower.includes('storm')) {
    return <CloudRain className="w-6 h-6 text-blue-400" />
  }
  if (lower.includes('cloud') || lower.includes('overcast')) {
    return <Cloud className="w-6 h-6 text-ocean-300" />
  }
  if (isDaytime) {
    return <Sun className="w-6 h-6 text-lava-400" />
  }
  return <Moon className="w-6 h-6 text-ocean-300" />
}

export default function ForecastBar({ forecasts }: ForecastBarProps) {
  // Show first 8 periods (about 4 days)
  const visible = forecasts.slice(0, 8)

  return (
    <div className="overflow-x-auto pb-2 -mx-4 px-4">
      <div className="flex gap-3 min-w-max">
        {visible.map((period, idx) => (
          <div
            key={idx}
            className="flex flex-col items-center gap-1.5 px-4 py-3 rounded-xl bg-ocean-800/40 border border-ocean-700/30 min-w-[90px]"
          >
            <span className="text-ocean-400 text-xs font-medium whitespace-nowrap">
              {period.name}
            </span>
            {getForecastIcon(period.short_forecast, period.is_daytime)}
            <span className="text-white font-display font-bold text-lg">
              {period.temperature}°
            </span>
            <span className="text-ocean-400 text-xs text-center leading-tight max-w-[80px]">
              {period.short_forecast}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
