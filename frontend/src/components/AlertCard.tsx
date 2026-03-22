/**
 * Displays a single weather alert (warning, watch, advisory).
 *
 * Severity levels control the visual urgency:
 *   Extreme = red pulse, Severe = orange, Moderate = amber, Minor = green
 */

import { useState } from 'react'
import { AlertTriangle, Clock, MapPin, ChevronDown, ChevronUp } from 'lucide-react'
import type { WeatherAlert, AlertSeverity } from '../utils/types'

interface AlertCardProps {
  alert: WeatherAlert
}

const severityConfig: Record<AlertSeverity, { badge: string; icon: string }> = {
  extreme: { badge: 'badge-extreme', icon: 'text-red-400' },
  severe: { badge: 'badge-severe', icon: 'text-orange-400' },
  moderate: { badge: 'badge-moderate', icon: 'text-amber-400' },
  minor: { badge: 'badge-minor', icon: 'text-lime-400' },
  unknown: { badge: 'badge-moderate', icon: 'text-ocean-400' },
}

export default function AlertCard({ alert }: AlertCardProps) {
  const [expanded, setExpanded] = useState(false)
  const config = severityConfig[alert.severity] || severityConfig.unknown

  // Format expiry time
  const expiresAt = alert.expires
    ? new Date(alert.expires).toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      })
    : null

  return (
    <div
      className="card border-l-4 border-l-alert-moderate cursor-pointer hover:border-ocean-600/50 transition-colors"
      onClick={() => setExpanded(e => !e)}
      style={{
        borderLeftColor: alert.severity === 'extreme' ? '#dc2626'
          : alert.severity === 'severe' ? '#ea580c'
          : alert.severity === 'moderate' ? '#d97706'
          : '#65a30d'
      }}
    >
      {/* Top: icon + headline + severity badge */}
      <div className="flex items-start gap-3 mb-2">
        <AlertTriangle className={`w-5 h-5 mt-0.5 flex-shrink-0 ${config.icon}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h3 className="font-display font-semibold text-sm text-white leading-tight">
              {alert.headline}
            </h3>
            <span className={`flex-shrink-0 ${config.badge}`}>
              {alert.severity}
            </span>
          </div>

          {/* Description */}
          <p className={`text-ocean-300 text-sm leading-relaxed ${expanded ? '' : 'line-clamp-3'}`}>
            {alert.description}
          </p>
        </div>

        {/* Expand toggle */}
        <div className="flex-shrink-0 text-ocean-500 mt-0.5">
          {expanded
            ? <ChevronUp className="w-4 h-4" />
            : <ChevronDown className="w-4 h-4" />
          }
        </div>
      </div>

      {/* Bottom: areas + expiry */}
      <div className="flex items-center gap-4 text-ocean-400 text-xs mt-3 ml-8">
        {alert.areas && (
          <span className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {alert.areas}
          </span>
        )}
        {expiresAt && (
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Expires {expiresAt}
          </span>
        )}
      </div>
    </div>
  )
}
