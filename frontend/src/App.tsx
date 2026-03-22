/**
 * Maui Alert Hub - Main App Component
 *
 * This is the top-level component that composes the full dashboard.
 * It fetches road and weather data, then renders the sections.
 */

import { useState, useCallback, useEffect } from 'react'
import { MapPin, CloudLightning, Route, Activity } from 'lucide-react'
import Header from './components/Header'
import RoadCard from './components/RoadCard'
import AlertCard from './components/AlertCard'
import ForecastBar from './components/ForecastBar'
import EarthquakeCard from './components/EarthquakeCard'
import ChecklistSection from './components/ChecklistSection'
import { LoadingSpinner, ErrorMessage, EmptyState } from './components/StatusStates'
import { useApi } from './hooks/useApi'
import { getRoadClosures, getWeather, getEarthquakes } from './utils/api'
import { timeAgo } from './utils/time'

export default function App() {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  // Fetch road closures
  const roads = useApi(getRoadClosures)

  // Fetch weather (alerts + forecast)
  const weather = useApi(getWeather)

  // Fetch earthquakes
  const quakes = useApi(getEarthquakes)

  // Refresh all data
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true)
    await Promise.all([roads.refresh(), weather.refresh(), quakes.refresh()])
    setIsRefreshing(false)
  }, [roads, weather, quakes])

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      roads.refresh()
      weather.refresh()
      quakes.refresh()
    }, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [roads.refresh, weather.refresh, quakes.refresh])

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

  return (
    <div className="min-h-screen bg-ocean-900">
      <Header onRefresh={handleRefresh} isRefreshing={isRefreshing} />

      {!isOnline && (
        <div className="bg-amber-900/80 border-b border-amber-700/50 px-4 py-2 text-center">
          <p className="text-amber-300 text-sm">
            You're offline. Showing cached data.
          </p>
        </div>
      )}

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-8">

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
            <div className="card bg-green-900/20 border-green-700/30">
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
            <div className="card bg-ocean-800/20 border-ocean-700/20">
              <p className="text-ocean-400 text-sm text-center py-2">
                No earthquakes above M2.5 near Hawaii recently.
              </p>
            </div>
          )}
        </section>

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
                <RoadCard key={road.id || idx} road={road} />
              ))}
            </div>
          ) : (
            <EmptyState message="No road closures reported. Drive safe!" />
          )}
        </section>

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
