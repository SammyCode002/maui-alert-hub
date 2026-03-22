/**
 * App header with logo, title, and last-updated timestamp.
 */

import { RefreshCw, Activity } from 'lucide-react'
import NotificationButton from './NotificationButton'

interface HeaderProps {
  onRefresh: () => void
  isRefreshing: boolean
}

export default function Header({ onRefresh, isRefreshing }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-black/20 backdrop-blur-xl border-b border-white/[0.07]">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo + Title */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-ocean-400 to-ocean-700 flex items-center justify-center shadow-lg shadow-ocean-500/30 ring-1 ring-white/10">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-display font-bold text-lg leading-tight text-gradient">
              Maui Alert Hub
            </h1>
            <p className="text-ocean-500 text-xs">
              Roads, weather, and alerts
            </p>
          </div>
        </div>

        {/* Right side: notification bell + refresh */}
        <div className="flex items-center gap-2">
        <NotificationButton />
        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2.5 rounded-xl bg-ocean-800/60 border border-ocean-700/50 hover:bg-ocean-700/60 transition-colors disabled:opacity-50"
          aria-label="Refresh data"
        >
          <RefreshCw
            className={`w-4 h-4 text-ocean-300 ${isRefreshing ? 'animate-spin' : ''}`}
          />
        </button>
        </div>
      </div>
    </header>
  )
}
