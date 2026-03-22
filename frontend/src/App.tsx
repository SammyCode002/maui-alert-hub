/**
 * Maui Alert Hub - Main App Component
 *
 * This is the top-level component that composes the full dashboard.
 * It fetches road and weather data, then renders the sections.
 */

import { useState, useCallback } from 'react'
import { MapPin, CloudLightning, Route } from 'lucide-react'
import Header from './components/Header'
import RoadCard from './components/RoadCard'
import AlertCard from './components/AlertCard'
import ForecastBar from './components/ForecastBar'
import { LoadingSpinner, ErrorMessage, EmptyState } from './components/StatusStates'
import { useApi } from './hooks/useApi'
import { getRoadClosures, getWeather } from './utils/api'

export default function App() {
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Fetch road closures
  const roads = useApi(getRoadClosures)

  // Fetch weather (alerts + forecast)
  const weather = useApi(getWeather)

  // Refresh all data
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true)
    await Promise.all([roads.refresh(), weather.refresh()])
    setIsRefreshing(false)
  }, [roads, weather])

  // Count active alerts for the badge
  const alertCount = weather.data?.alerts?.length ?? 0

  return (
    <div className="min-h-screen bg-ocean-900">
      <Header onRefresh={handleRefresh} isRefreshing={isRefreshing} />

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
