/**
 * Displays a single tsunami alert with urgent red styling.
 *
 * Tsunami Warning  = most severe, evacuate now (extreme red)
 * Tsunami Watch    = threat possible, be ready (severe orange-red)
 * Tsunami Advisory = strong currents (moderate amber)
 * Info Statement   = no threat, informational (neutral)
 */

import { useState } from 'react'
import { Waves, ChevronDown, ChevronUp } from 'lucide-react'
import type { TsunamiAlert } from '../utils/types'
import { timeAgo } from '../utils/time'

interface TsunamiCardProps {
  alert: TsunamiAlert
}

const eventConfig: Record<string, { border: string; glow: string; badge: string; badgeText: string }> = {
  warning:  { border: '#dc2626', glow: 'rgba(220,38,38,0.25)',  badge: 'bg-red-500/20 text-red-300',    badgeText: 'WARNING' },
  watch:    { border: '#ea580c', glow: 'rgba(234,88,12,0.20)',  badge: 'bg-orange-500/20 text-orange-300', badgeText: 'WATCH' },
  advisory: { border: '#d97706', glow: 'rgba(217,119,6,0.18)', badge: 'bg-amber-500/20 text-amber-300', badgeText: 'ADVISORY' },
  default:  { border: '#0891b2', glow: 'rgba(8,145,178,0.12)', badge: 'bg-cyan-500/20 text-cyan-300',   badgeText: 'INFO' },
}

function getConfig(event: string) {
  const lower = event.toLowerCase()
  if (lower.includes('warning'))  return eventConfig.warning
  if (lower.includes('watch'))    return eventConfig.watch
  if (lower.includes('advisory')) return eventConfig.advisory
  return eventConfig.default
}

export default function TsunamiCard({ alert }: TsunamiCardProps) {
  const [expanded, setExpanded] = useState(false)
  const cfg = getConfig(alert.event)

  return (
    <div
      className="card border-l-4 cursor-pointer hover:brightness-110 transition-all"
      style={{ borderLeftColor: cfg.border, boxShadow: `0 0 24px ${cfg.glow}, 0 4px 20px rgba(0,0,0,0.4)` }}
      onClick={() => setExpanded(e => !e)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Waves className="w-4 h-4 flex-shrink-0" style={{ color: cfg.border }} />
          <p className="font-display font-semibold text-white text-sm leading-snug">
            {alert.headline}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${cfg.badge}`}>
            {cfg.badgeText}
          </span>
          {expanded
            ? <ChevronUp className="w-4 h-4 text-ocean-500" />
            : <ChevronDown className="w-4 h-4 text-ocean-500" />
          }
        </div>
      </div>

      {alert.areas && (
        <p className="text-ocean-400 text-xs mt-1.5">Affects: {alert.areas}</p>
      )}

      {expanded && alert.description && (
        <p className="text-ocean-300 text-xs mt-3 leading-relaxed whitespace-pre-line border-t border-white/[0.06] pt-3">
          {alert.description}
        </p>
      )}

      <div className="flex items-center gap-3 mt-2 text-ocean-600 text-xs">
        {alert.onset && <span>Onset {timeAgo(alert.onset)}</span>}
        {alert.expires && <span>Expires {timeAgo(alert.expires)}</span>}
        <span className="ml-auto">NWS/PTWC</span>
      </div>
    </div>
  )
}
