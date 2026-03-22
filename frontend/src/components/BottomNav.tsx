/**
 * Bottom navigation bar — 5 tabs that switch between dashboard sections.
 * Shows a red badge on the Alerts tab when there are active alerts.
 */

import { TriangleAlert, Route, Cloud, Activity, ShieldCheck } from 'lucide-react'

export type NavTab = 'alerts' | 'roads' | 'weather' | 'activity' | 'prep'

interface BottomNavProps {
  active: NavTab
  onChange: (tab: NavTab) => void
  alertBadge?: number
}

const TABS: Array<{ id: NavTab; label: string; Icon: React.FC<{ className?: string }> }> = [
  { id: 'alerts',   label: 'Alerts',   Icon: TriangleAlert },
  { id: 'roads',    label: 'Roads',    Icon: Route },
  { id: 'weather',  label: 'Weather',  Icon: Cloud },
  { id: 'activity', label: 'Activity', Icon: Activity },
  { id: 'prep',     label: 'Prep',     Icon: ShieldCheck },
]

export default function BottomNav({ active, onChange, alertBadge = 0 }: BottomNavProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-black/40 backdrop-blur-xl border-t border-white/[0.07]">
      <div className="max-w-4xl mx-auto flex">
        {TABS.map(({ id, label, Icon }) => {
          const isActive = active === id
          const hasBadge = id === 'alerts' && alertBadge > 0

          return (
            <button
              key={id}
              onClick={() => onChange(id)}
              className={`flex-1 flex flex-col items-center gap-1 py-2.5 transition-colors relative ${
                isActive ? 'text-ocean-300' : 'text-ocean-600 hover:text-ocean-400'
              }`}
            >
              <div className="relative">
                <Icon className="w-5 h-5" />
                {hasBadge && (
                  <span className="absolute -top-1 -right-1.5 bg-red-500 text-white text-[9px] font-bold w-4 h-4 rounded-full flex items-center justify-center leading-none">
                    {alertBadge > 9 ? '9+' : alertBadge}
                  </span>
                )}
              </div>
              <span className="text-[10px] font-medium leading-none">{label}</span>
              {isActive && (
                <span className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-ocean-400 rounded-full" />
              )}
            </button>
          )
        })}
      </div>
      {/* Safe area padding for iOS home indicator */}
      <div className="h-safe-bottom bg-transparent" />
    </nav>
  )
}
