/**
 * Displays a single road closure/restriction as a card.
 *
 * The status badge color tells you at a glance:
 *   Red = Closed, Amber = Restricted, Green = Open
 */

import { MapPin, Clock, Star } from 'lucide-react'
import type { RoadClosure, RoadStatus } from '../utils/types'

interface RoadCardProps {
  road: RoadClosure
  isSaved?: boolean
  onToggleSave?: (id: string) => void
}

const statusConfig: Record<RoadStatus, { badge: string; label: string }> = {
  closed: { badge: 'badge-closed', label: 'Closed' },
  restricted: { badge: 'badge-restricted', label: 'Restricted' },
  open: { badge: 'badge-open', label: 'Open' },
  unknown: { badge: 'badge-restricted', label: 'Unknown' },
}

export default function RoadCard({ road, isSaved = false, onToggleSave }: RoadCardProps) {
  const config = statusConfig[road.status] || statusConfig.unknown

  // Format the timestamp to something readable
  const updatedTime = road.updated_at
    ? new Date(road.updated_at).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      })
    : 'Unknown'

  return (
    <div className="card hover:brightness-110 transition-all">
      {/* Top row: road name + status badge + save star */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <h3 className="font-display font-semibold text-base text-white leading-tight flex-1">
          {road.road_name}
        </h3>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={config.badge}>{config.label}</span>
          {onToggleSave && road.id && (
            <button
              onClick={e => { e.stopPropagation(); onToggleSave(road.id!) }}
              className="text-ocean-600 hover:text-amber-400 transition-colors"
              aria-label={isSaved ? 'Unsave route' : 'Save route'}
            >
              <Star className={`w-4 h-4 ${isSaved ? 'fill-amber-400 text-amber-400' : ''}`} />
            </button>
          )}
        </div>
      </div>

      {/* Bottom row: location + timestamp */}
      <div className="flex items-center gap-4 text-ocean-400 text-xs">
        {road.location && (
          <span className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {road.location}
          </span>
        )}
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {updatedTime}
        </span>
      </div>
    </div>
  )
}
