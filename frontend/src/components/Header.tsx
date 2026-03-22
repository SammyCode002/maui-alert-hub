/**
 * App header with logo, title, and last-updated timestamp.
 */

import { RefreshCw, Activity } from 'lucide-react'

interface HeaderProps {
  onRefresh: () => void
  isRefreshing: boolean
}

export default function Header({ onRefresh, isRefreshing }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-ocean-900/80 backdrop-blur-md border-b border-ocean-700/50">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo + Title */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-ocean-400 to-ocean-600 flex items-center justify-center shadow-lg shadow-ocean-500/20">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-display font-bold text-lg leading-tight">
              Maui Alert Hub
            </h1>
            <p className="text-ocean-400 text-xs">
              Roads, weather, and alerts
            </p>
          </div>
        </div>

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
    </header>
  )
}
