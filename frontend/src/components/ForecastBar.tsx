/**
 * Horizontal scrollable forecast bar showing upcoming weather periods.
 * Each tile gets a gradient background based on the weather condition.
 */

import { Sun, Moon, CloudRain, Cloud, CloudLightning, Wind } from 'lucide-react'
import type { WeatherForecast } from '../utils/types'

interface ForecastBarProps {
  forecasts: WeatherForecast[]
}

function getForecastIcon(forecast: string, isDaytime: boolean) {
  const lower = forecast.toLowerCase()
  if (lower.includes('storm') || lower.includes('thunder')) {
    return <CloudLightning className="w-7 h-7 text-purple-300" />
  }
  if (lower.includes('rain') || lower.includes('shower')) {
    return <CloudRain className="w-7 h-7 text-blue-300" />
  }
  if (lower.includes('wind') || lower.includes('breezy') || lower.includes('blustery')) {
    return <Wind className="w-7 h-7 text-cyan-300" />
  }
  if (lower.includes('cloud') || lower.includes('overcast')) {
    return <Cloud className="w-7 h-7 text-slate-300" />
  }
  if (isDaytime) {
    return <Sun className="w-7 h-7 text-amber-300" />
  }
  return <Moon className="w-7 h-7 text-ocean-200" />
}

function getTileClasses(forecast: string, isDaytime: boolean): string {
  const lower = forecast.toLowerCase()
  if (lower.includes('storm') || lower.includes('thunder')) {
    return 'bg-gradient-to-b from-purple-900/60 to-slate-900/70 border-purple-700/30'
  }
  if (lower.includes('rain') || lower.includes('shower')) {
    return 'bg-gradient-to-b from-blue-900/60 to-slate-900/70 border-blue-700/30'
  }
  if (lower.includes('wind') || lower.includes('breezy')) {
    return 'bg-gradient-to-b from-cyan-900/50 to-ocean-900/60 border-cyan-700/20'
  }
  if (lower.includes('cloud') || lower.includes('overcast')) {
    return 'bg-gradient-to-b from-slate-700/50 to-ocean-900/60 border-slate-600/20'
  }
  if (isDaytime) {
    return 'bg-gradient-to-b from-sky-800/50 to-ocean-900/60 border-sky-600/20'
  }
  return 'bg-gradient-to-b from-[#0a1628]/80 to-ocean-900/70 border-ocean-700/20'
}

export default function ForecastBar({ forecasts }: ForecastBarProps) {
  const visible = forecasts.slice(0, 8)

  return (
    <div className="overflow-x-auto pb-2 -mx-4 px-4">
      <div className="flex gap-2.5 min-w-max">
        {visible.map((period, idx) => (
          <div
            key={idx}
            className={`flex flex-col items-center gap-2 px-4 py-3.5 rounded-2xl border min-w-[88px] transition-transform hover:scale-[1.03] ${getTileClasses(period.short_forecast, period.is_daytime)}`}
          >
            <span className="text-white/50 text-xs font-medium whitespace-nowrap">
              {period.name}
            </span>
            {getForecastIcon(period.short_forecast, period.is_daytime)}
            <span className="text-white font-display font-bold text-xl leading-none">
              {period.temperature}°
            </span>
            <span className="text-white/40 text-[11px] text-center leading-tight max-w-[76px]">
              {period.short_forecast}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
