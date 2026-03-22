/**
 * Displays a single earthquake event from the USGS.
 *
 * Magnitude color coding:
 *   5.0+ = red (potentially damaging)
 *   4.0-4.9 = orange (widely felt)
 *   3.0-3.9 = amber (felt by some)
 *   < 3.0 = muted (rarely felt)
 */

import { Clock, ArrowDown, ExternalLink } from 'lucide-react'
import type { Earthquake } from '../utils/types'
import { timeAgo } from '../utils/time'

interface EarthquakeCardProps {
  quake: Earthquake
}

function getMagColor(mag: number): string {
  if (mag >= 5.0) return 'text-red-400'
  if (mag >= 4.0) return 'text-orange-400'
  if (mag >= 3.0) return 'text-amber-400'
  return 'text-ocean-400'
}

function getCardStyle(mag: number): string {
  if (mag >= 5.0) return 'border-red-700/40 bg-red-900/10'
  if (mag >= 4.0) return 'border-orange-700/30 bg-orange-900/10'
  if (mag >= 3.0) return 'border-amber-700/20 bg-amber-900/5'
  return 'border-ocean-700/30'
}

export default function EarthquakeCard({ quake }: EarthquakeCardProps) {
  const ago = timeAgo(quake.time)

  return (
    <div className={`card border ${getCardStyle(quake.magnitude)}`}>
      <div className="flex items-center gap-4">
        {/* Magnitude badge */}
        <div className="flex-shrink-0 text-center w-12">
          <span className={`font-display font-bold text-2xl leading-none ${getMagColor(quake.magnitude)}`}>
            {quake.magnitude.toFixed(1)}
          </span>
          <p className="text-ocean-500 text-xs mt-0.5">mag</p>
        </div>

        {/* Details */}
        <div className="flex-1 min-w-0">
          <p className="text-white text-sm font-medium leading-tight">
            {quake.place}
          </p>
          <div className="flex items-center gap-3 mt-1 text-ocean-400 text-xs">
            {ago && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {ago}
              </span>
            )}
            <span className="flex items-center gap-1">
              <ArrowDown className="w-3 h-3" />
              {quake.depth_km} km deep
            </span>
          </div>
        </div>

        {/* USGS link */}
        {quake.url && (
          <a
            href={quake.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-shrink-0 text-ocean-500 hover:text-ocean-300 transition-colors"
            aria-label="View on USGS"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  )
}
