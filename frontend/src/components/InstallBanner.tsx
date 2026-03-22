/**
 * PWA install prompt banner.
 *
 * Slides up from the bottom of the screen.
 * Android/Chrome: shows an "Install" button that triggers the native prompt.
 * iOS Safari: shows "Add to Home Screen" instructions since iOS has no install API.
 * Disappears once installed or dismissed (dismissal persists via localStorage).
 */

import { Activity, X, Download, ArrowUpFromLine } from 'lucide-react'
import { useInstallPrompt } from '../hooks/useInstallPrompt'

export default function InstallBanner() {
  const { showBanner, isIOS, install, dismiss } = useInstallPrompt()

  if (!showBanner) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 px-4 pb-6 pt-2 animate-slide-up">
      <div className="max-w-4xl mx-auto">
        <div
          className="card flex items-center gap-3 border-ocean-500/20"
          style={{ boxShadow: '0 8px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.06)' }}
        >
          {/* App icon */}
          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-ocean-400 to-ocean-700 flex items-center justify-center flex-shrink-0 ring-1 ring-white/10 shadow-lg shadow-ocean-500/20">
            <Activity className="w-5 h-5 text-white" />
          </div>

          {/* Text */}
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-semibold leading-tight">
              Install Maui Alert Hub
            </p>
            {isIOS ? (
              <p className="text-ocean-400 text-xs mt-0.5 leading-snug">
                Tap <ArrowUpFromLine className="w-3 h-3 inline mb-0.5" /> Share, then
                {' '}<span className="text-ocean-300 font-medium">Add to Home Screen</span>
              </p>
            ) : (
              <p className="text-ocean-400 text-xs mt-0.5">
                Add to home screen for instant access
              </p>
            )}
          </div>

          {/* Install button — Android only (iOS has no install API) */}
          {!isIOS && (
            <button
              onClick={install}
              className="flex-shrink-0 flex items-center gap-1.5 bg-ocean-400 hover:bg-ocean-300 text-ocean-950 text-xs font-bold px-3.5 py-2 rounded-xl transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Install
            </button>
          )}

          {/* Dismiss */}
          <button
            onClick={dismiss}
            className="flex-shrink-0 p-1.5 text-ocean-600 hover:text-ocean-300 transition-colors rounded-lg hover:bg-white/5"
            aria-label="Dismiss install prompt"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
