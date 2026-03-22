/**
 * Maui Alert Hub - Main App Component
 *
 * This is the top-level component that composes the full dashboard.
 * It fetches road and weather data, then renders the sections.
 */

import { useState, useCallback, useEffect } from 'react'
import { MapPin, CloudLightning, Route, Activity, Flame, Waves, Megaphone } from 'lucide-react'
import Header from './components/Header'
import RoadCard from './components/RoadCard'
import AlertCard from './components/AlertCard'
import ForecastBar from './components/ForecastBar'
import EarthquakeCard from './components/EarthquakeCard'
import VolcanicCard from './components/VolcanicCard'
import SurfCard from './components/SurfCard'
import ChecklistSection from './components/ChecklistSection'
import InstallBanner from './components/InstallBanner'
import AdminPage from './components/AdminPage'
import { LoadingSpinner, ErrorMessage, EmptyState } from './components/StatusStates'
import { useApi } from './hooks/useApi'
import { useSavedRoutes } from './hooks/useSavedRoutes'
import { getRoadClosures, getWeather, getEarthquakes, getVolcanic, getSurf, getCommunityAlerts } from './utils/api'
import { timeAgo } from './utils/time'
import type { CommunityAlert } from './utils/types'

export default function App() {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [page, setPage] = useState<'home' | 'admin'>(() =>
    window.location.hash === '#admin' ? 'admin' : 'home'
  )

  // Hash-based routing (no React Router needed)
  useEffect(() => {
    const onHash = () => setPage(window.location.hash === '#admin' ? 'admin' : 'home')
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  // Saved routes
  const { isSaved, toggle: toggleSaved } = useSavedRoutes()

  // Data fetching
  const roads = useApi(getRoadClosures)
  const weather = useApi(getWeather)
  const quakes = useApi(getEarthquakes)
  const volcanic = useApi(getVolcanic)
  const surf = useApi(getSurf)
  const community = useApi(getCommunityAlerts)

  // Refresh all data
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true)
    await Promise.all([
      roads.refresh(), weather.refresh(), quakes.refresh(),
      volcanic.refresh(), surf.refresh(), community.refresh(),
    ])
    setIsRefreshing(false)
  }, [roads, weather, quakes, volcanic, surf, community])

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      roads.refresh()
      weather.refresh()
      quakes.refresh()
      volcanic.refresh()
      surf.refresh()
      community.refresh()
    }, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [roads.refresh, weather.refresh, quakes.refresh, volcanic.refresh, surf.refresh, community.refresh])

  // Track online/offline status
  useEffect(() => {
    const onOnline = () => setIsOnline(true)
    const onOffline = () => setIsOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  // Count active alerts for the badge
  const alertCount = weather.data?.alerts?.length ?? 0

  if (page === 'admin') return <AdminPage />

  // Active community alerts (non-null, already filtered by backend)
  const communityAlerts: CommunityAlert[] = community.data?.alerts ?? []

  return (
    <div className="min-h-screen">
      {/* Ambient background orbs */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] rounded-full bg-ocean-500/10 blur-[120px] translate-x-1/3 -translate-y-1/4" />
        <div className="absolute top-1/2 left-0 w-[500px] h-[500px] rounded-full bg-cyan-900/20 blur-[100px] -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] rounded-full bg-ocean-700/15 blur-[90px] translate-y-1/3" />
      </div>

      <Header onRefresh={handleRefresh} isRefreshing={isRefreshing} />
      <InstallBanner />

      {!isOnline && (
        <div className="bg-amber-500/10 backdrop-blur-sm border-b border-amber-500/20 px-4 py-2 text-center">
          <p className="text-amber-300 text-sm">
            You're offline. Showing cached data.
          </p>
        </div>
      )}

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-8">

        {/* ============================================= */}
        {/* COMMUNITY ALERTS (admin-posted)               */}
        {/* ============================================= */}
        {communityAlerts.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Megaphone className="w-5 h-5 text-red-400" />
              <h2 className="font-display font-bold text-lg">Community Alerts</h2>
              <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-0.5 rounded-full">
                {communityAlerts.length}
              </span>
            </div>
            <div className="space-y-3">
              {communityAlerts.map(alert => {
                const colors = {
                  danger:  { border: '#dc2626', glow: 'rgba(220,38,38,0.2)' },
                  warning: { border: '#d97706', glow: 'rgba(217,119,6,0.15)' },
                  info:    { border: '#0891b2', glow: 'rgba(8,145,178,0.1)' },
                }
                const c = colors[alert.severity] ?? colors.warning
                return (
                  <div key={alert.id} className="card border-l-4" style={{ borderLeftColor: c.border, boxShadow: `0 0 20px ${c.glow}, 0 4px 20px rgba(0,0,0,0.4)` }}>
                    <p className="font-display font-semibold text-white text-sm">{alert.title}</p>
                    <p className="text-ocean-300 text-sm mt-1">{alert.message}</p>
                    {alert.expires_at && (
                      <p className="text-ocean-500 text-xs mt-2">Expires {timeAgo(alert.expires_at)}</p>
                    )}
                  </div>
                )
              })}
            </div>
          </section>
        )}

        {/* ============================================= */}
        {/* WEATHER ALERTS SECTION                        */}
        {/* ============================================= */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <CloudLightning className="w-5 h-5 text-lava-400" />
            <h2 className="font-display font-bold text-lg">Weather Alerts</h2>
            {alertCount > 0 && (
              <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-0.5 rounded-full">
                {alertCount} active
              </span>
            )}
            {timeAgo(weather.data?.last_updated) && (
              <span className="ml-auto text-ocean-600 text-xs">
                {timeAgo(weather.data?.last_updated)}
              </span>
            )}
          </div>

          {weather.loading ? (
            <LoadingSpinner message="Checking NWS alerts..." />
          ) : weather.error ? (
            <ErrorMessage message={weather.error} onRetry={weather.refresh} />
          ) : weather.data?.alerts && weather.data.alerts.length > 0 ? (
            <div className="space-y-3">
              {weather.data.alerts.map((alert, idx) => (
                <AlertCard key={alert.id || idx} alert={alert} />
              ))}
            </div>
          ) : (
            <div className="card border-green-500/20" style={{ boxShadow: '0 0 20px rgba(34,197,94,0.08), 0 4px 20px rgba(0,0,0,0.3)' }}>
              <p className="text-green-400 text-sm text-center py-2">
                No active weather alerts for Maui. All clear!
              </p>
            </div>
          )}
        </section>

        {/* ============================================= */}
        {/* FORECAST BAR                                  */}
        {/* ============================================= */}
        {weather.data?.forecasts && weather.data.forecasts.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="w-5 h-5 text-ocean-400" />
              <h2 className="font-display font-bold text-lg">Forecast</h2>
              <span className="text-ocean-500 text-xs">Kahului, Maui</span>
            </div>
            <ForecastBar forecasts={weather.data.forecasts} />
          </section>
        )}

        {/* ============================================= */}
        {/* ROAD CLOSURES SECTION                         */}
        {/* ============================================= */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Route className="w-5 h-5 text-lava-400" />
            <h2 className="font-display font-bold text-lg">Road Closures</h2>
            {roads.data && roads.data.total > 0 && (
              <span className="bg-lava-500/20 text-lava-400 text-xs font-bold px-2 py-0.5 rounded-full">
                {roads.data.total} reported
              </span>
            )}
            {timeAgo(roads.data?.last_scraped) && (
              <span className="ml-auto text-ocean-600 text-xs">
                {timeAgo(roads.data?.last_scraped)}
              </span>
            )}
          </div>

          {roads.loading ? (
            <LoadingSpinner message="Checking road conditions..." />
          ) : roads.error ? (
            <ErrorMessage message={roads.error} onRetry={roads.refresh} />
          ) : roads.data?.roads && roads.data.roads.length > 0 ? (
            <div className="space-y-3">
              {roads.data.roads.map((road, idx) => (
                <RoadCard
                  key={road.id || idx}
                  road={road}
                  isSaved={road.id ? isSaved(road.id) : false}
                  onToggleSave={road.id ? toggleSaved : undefined}
                />
              ))}
            </div>
          ) : (
            <EmptyState message="No road closures reported. Drive safe!" />
          )}
        </section>

        {/* ============================================= */}
        {/* EARTHQUAKE SECTION                            */}
        {/* ============================================= */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-ocean-400" />
            <h2 className="font-display font-bold text-lg">Recent Earthquakes</h2>
            {quakes.data && quakes.data.total > 0 && (
              <span className="bg-ocean-700/40 text-ocean-300 text-xs font-bold px-2 py-0.5 rounded-full">
                {quakes.data.total} nearby
              </span>
            )}
            <span className="text-ocean-500 text-xs ml-1">M2.5+, 300km radius</span>
          </div>

          {quakes.loading ? (
            <LoadingSpinner message="Checking USGS earthquake feed..." />
          ) : quakes.error ? (
            <ErrorMessage message={quakes.error} onRetry={quakes.refresh} />
          ) : quakes.data?.earthquakes && quakes.data.earthquakes.length > 0 ? (
            <div className="space-y-3">
              {quakes.data.earthquakes.map(quake => (
                <EarthquakeCard key={quake.id} quake={quake} />
              ))}
            </div>
          ) : (
            <div className="card border-ocean-700/20">
              <p className="text-ocean-400 text-sm text-center py-2">
                No earthquakes above M2.5 near Hawaii recently.
              </p>
            </div>
          )}
        </section>

        {/* ============================================= */}
        {/* VOLCANIC ACTIVITY SECTION                     */}
        {/* ============================================= */}
        {volcanic.data?.alerts && volcanic.data.alerts.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Flame className="w-5 h-5 text-orange-400" />
              <h2 className="font-display font-bold text-lg">Volcanic Activity</h2>
              <span className="text-ocean-500 text-xs ml-1">Hawaii volcanoes</span>
            </div>
            <div className="space-y-3">
              {volcanic.data.alerts.map(alert => (
                <VolcanicCard key={alert.id} alert={alert} />
              ))}
            </div>
          </section>
        )}

        {/* ============================================= */}
        {/* SURF REPORT SECTION                           */}
        {/* ============================================= */}
        {surf.data?.spots && surf.data.spots.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Waves className="w-5 h-5 text-ocean-400" />
              <h2 className="font-display font-bold text-lg">Surf Report</h2>
              <span className="text-ocean-500 text-xs ml-1">NOAA buoy data</span>
              {timeAgo(surf.data.last_updated) && (
                <span className="ml-auto text-ocean-600 text-xs">
                  {timeAgo(surf.data.last_updated)}
                </span>
              )}
            </div>
            <div className="space-y-3">
              {surf.data.spots.map(spot => (
                <SurfCard key={spot.buoy_id} spot={spot} />
              ))}
            </div>
          </section>
        )}

        {/* ============================================= */}
        {/* EMERGENCY PREP CHECKLIST                      */}
        {/* ============================================= */}
        <ChecklistSection />

        {/* ============================================= */}
        {/* FOOTER                                        */}
        {/* ============================================= */}
        <footer className="text-center text-ocean-500 text-xs py-8 border-t border-ocean-800">
          <p>
            Maui Alert Hub v0.1.0
          </p>
          <p className="mt-1">
            Data from Maui County and the National Weather Service.
            Not an official government source.
          </p>
        </footer>
      </main>
    </div>
  )
}
