/**
 * Hawaii Emergency Prep Checklist.
 *
 * A collapsible checklist with localStorage persistence.
 * Based on Hawaii Emergency Management Agency recommended supplies.
 */

import { useState } from 'react'
import { ShieldCheck, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react'
import { useChecklist } from '../hooks/useChecklist'

const PREP_ITEMS = [
  '3-day water supply (1 gal/person/day)',
  '3-day non-perishable food supply',
  'Manual can opener',
  'First aid kit',
  '7-day supply of medications',
  'Flashlights and extra batteries',
  'Battery-powered NOAA weather radio',
  'Whistle to signal for help',
  'Portable phone charger / power bank',
  'Cash in small bills',
  'Copies of important documents',
  'Extra clothing and sturdy shoes',
  'Sleeping bags or warm blankets',
  'Hurricane shutters or plywood for windows',
  'Full tank of gas',
]

export default function ChecklistSection() {
  const [open, setOpen] = useState(false)
  const { checked, toggle, reset, checkedCount } = useChecklist(PREP_ITEMS)
  const total = PREP_ITEMS.length
  const pct = Math.round((checkedCount / total) * 100)
  const allDone = checkedCount === total

  return (
    <section>
      <button
        className="flex items-center gap-2 mb-4 w-full text-left"
        onClick={() => setOpen(o => !o)}
      >
        <ShieldCheck className="w-5 h-5 text-lava-400" />
        <h2 className="font-display font-bold text-lg flex-1">Emergency Prep Checklist</h2>
        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
          allDone
            ? 'bg-green-500/20 text-green-400'
            : 'bg-lava-500/20 text-lava-400'
        }`}>
          {checkedCount}/{total}
        </span>
        {open
          ? <ChevronUp className="w-4 h-4 text-ocean-400" />
          : <ChevronDown className="w-4 h-4 text-ocean-400" />
        }
      </button>

      {open && (
        <div className="card space-y-3">
          {/* Progress bar */}
          <div className="h-1.5 rounded-full bg-ocean-700/50">
            <div
              className={`h-1.5 rounded-full transition-all duration-300 ${allDone ? 'bg-green-500' : 'bg-lava-500'}`}
              style={{ width: `${pct}%` }}
            />
          </div>

          {/* Items — 2 col on sm+ */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2.5">
            {PREP_ITEMS.map(item => (
              <label key={item} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={!!checked[item]}
                  onChange={() => toggle(item)}
                  className="w-4 h-4 rounded accent-lava-500 cursor-pointer flex-shrink-0"
                />
                <span className={`text-sm leading-tight ${
                  checked[item] ? 'line-through text-ocean-600' : 'text-ocean-200'
                }`}>
                  {item}
                </span>
              </label>
            ))}
          </div>

          {checkedCount > 0 && (
            <button
              onClick={reset}
              className="flex items-center gap-1.5 text-xs text-ocean-600 hover:text-ocean-400 transition-colors mt-1"
            >
              <RotateCcw className="w-3 h-3" />
              Reset all
            </button>
          )}
        </div>
      )}
    </section>
  )
}
