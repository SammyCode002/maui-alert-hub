/**
 * Displays current surf conditions from a NOAA NDBC buoy.
 *
 * Wave height is color-coded:
 *   6+ ft = red (large, experienced surfers)
 *   3-6 ft = amber (moderate)
 *   < 3 ft = ocean (small/flat)
 */

import { Waves } from 'lucide-react'
import type { SurfSpot } from '../utils/types'
import { timeAgo } from '../utils/time'

interface SurfCardProps {
  spot: SurfSpot
}

function getHeightColor(ft: number | null): string {
  if (ft === null) return 'text-ocean-400'
  if (ft >= 6) return 'text-red-400'
  if (ft >= 3) return 'text-amber-400'
  return 'text-ocean-300'
}

export default function SurfCard({ spot }: SurfCardProps) {
  const ago = timeAgo(spot.updated_at)

  return (
    <div className="card hover:brightness-110 transition-all">
      <div className="flex items-start justify-between gap-3">
        {/* Left: location */}
        <div className="flex items-center gap-2">
          <Waves className="w-5 h-5 text-ocean-400 flex-shrink-0" />
          <div>
            <h3 className="font-display font-semibold text-white text-sm leading-tight">
              {spot.name}
            </h3>
            <p className="text-ocean-500 text-xs">NDBC {spot.buoy_id}</p>
          </div>
        </div>

        {/* Right: wave height */}
        <div className="text-right flex-shrink-0">
          {spot.wave_height_ft !== null ? (
            <>
              <span className={`font-display font-bold text-2xl ${getHeightColor(spot.wave_height_ft)}`}>
                {spot.wave_height_ft}
              </span>
              <span className="text-ocean-400 text-sm ml-0.5">ft</span>
            </>
          ) : (
            <span className="text-ocean-600 text-sm">No data</span>
          )}
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 mt-3 pt-3 border-t border-white/[0.06]">
        <div>
          <p className="text-ocean-600 text-xs mb-0.5">Period</p>
          <p className="text-white text-sm font-medium">
            {spot.period_sec !== null ? `${spot.period_sec}s` : '—'}
          </p>
        </div>
        <div>
          <p className="text-ocean-600 text-xs mb-0.5">Direction</p>
          <p className="text-white text-sm font-medium">
            {spot.direction ?? '—'}
          </p>
        </div>
        <div>
          <p className="text-ocean-600 text-xs mb-0.5">Water</p>
          <p className="text-white text-sm font-medium">
            {spot.water_temp_f !== null ? `${spot.water_temp_f}°F` : '—'}
          </p>
        </div>
      </div>

      {ago && (
        <p className="text-ocean-600 text-xs mt-2">{ago}</p>
      )}
    </div>
  )
}
