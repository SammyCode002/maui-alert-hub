/**
 * Displays a USGS volcanic activity notification.
 *
 * Alert level color coding (mirrors USGS system):
 *   Warning / Red    = red
 *   Watch   / Orange = orange
 *   Advisory/ Yellow = amber
 *   Normal  / Green  = green (muted — no action needed)
 */

import { Flame } from 'lucide-react'
import type { VolcanicAlert } from '../utils/types'
import { timeAgo } from '../utils/time'

interface VolcanicCardProps {
  alert: VolcanicAlert
}

function getLevelColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'warning': return '#dc2626'
    case 'watch':   return '#ea580c'
    case 'advisory':return '#d97706'
    default:        return '#16a34a'
  }
}

function getAviationBadge(color: string): string {
  switch (color.toLowerCase()) {
    case 'red':    return 'bg-red-500/20 text-red-400 border-red-500/30'
    case 'orange': return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
    case 'yellow': return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    default:       return 'bg-green-500/20 text-green-400 border-green-500/30'
  }
}

export default function VolcanicCard({ alert }: VolcanicCardProps) {
  const borderColor = getLevelColor(alert.alert_level)
  const isNormal = alert.alert_level.toLowerCase() === 'normal'

  return (
    <div
      className="card border-l-4 transition-all hover:brightness-110"
      style={{
        borderLeftColor: borderColor,
        boxShadow: !isNormal
          ? `0 0 20px ${borderColor}22, 0 4px 20px rgba(0,0,0,0.4)`
          : '0 4px 20px rgba(0,0,0,0.3)',
      }}
    >
      <div className="flex items-start gap-3">
        <Flame
          className="w-5 h-5 mt-0.5 flex-shrink-0"
          style={{ color: borderColor }}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h3 className="font-display font-semibold text-sm text-white leading-tight">
              {alert.volcano_name}
            </h3>
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${getAviationBadge(alert.aviation_color)}`}>
                {alert.aviation_color}
              </span>
              <span className="text-xs font-bold text-white/60">
                {alert.alert_level}
              </span>
            </div>
          </div>
          <p className="text-ocean-300 text-sm leading-relaxed line-clamp-3">
            {alert.message}
          </p>
          <div className="flex items-center gap-3 mt-2 text-ocean-500 text-xs">
            <span>{timeAgo(alert.published)}</span>
            {alert.url && (
              <a
                href={alert.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-ocean-400 hover:text-ocean-200 transition-colors"
              >
                Full notice →
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
