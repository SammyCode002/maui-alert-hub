/**
 * Maui Alert Hub - Main App Component
 *
 * This is the top-level component that composes the full dashboard.
 * It fetches road and weather data, then renders the sections.
 */

import { useState, useCallback, useEffect } from 'react'
import { MapPin, CloudLightning, Route, Activity, Flame, Waves, Megaphone, Wind, TriangleAlert, Map, History, ChevronDown, ChevronUp } from 'lucide-react'
import Header from './components/Header'
import BottomNav from './components/BottomNav'
import type { NavTab } from './components/BottomNav'
import RoadCard from './components/RoadCard'
import AlertCard from './components/AlertCard'
import ForecastBar from './components/ForecastBar'
import EarthquakeCard from './components/EarthquakeCard'
import VolcanicCard from './components/VolcanicCard'
import SurfCard from './components/SurfCard'
import TsunamiCard from './components/TsunamiCard'
import AirQualityCard from './components/AirQualityCard'
import MapView from './components/MapView'
import ChecklistSection from './components/ChecklistSection'
import InstallBanner from './components/InstallBanner'
import AdminPage from './components/AdminPage'
import { LoadingSpinner, ErrorMessage, EmptyState } from './components/StatusStates'
import { useApi } from './hooks/useApi'
import { useSavedRoutes } from './hooks/useSavedRoutes'
import {
  getRoadClosures, getWeather, getEarthquakes, getVolcanic,
  getSurf, getCommunityAlerts, getTsunami, getAQI,
  getAlertHistory, syncSavedRoutes,
} from './utils/api'
import { timeAgo, isStale } from './utils/time'
import type { CommunityAlert, ForecastCityKey, AlertHistoryEntry } from './utils/types'
import { FORECAST_CITIES } from './utils/types'

// ============================================================
// Alert History Section (collapsed by default)
// ============================================================
function AlertHistorySection({ data }: { data: AlertHistoryEntry[] }) {
  const [expanded, setExpanded] = useState(false)
  if (data.length === 0) return null
  const severityColor: Record<string, string> = {
    extreme: 'text-red-400', severe: 'text-orange-400',
    moderate: 'text-amber-400', minor: 'text-lime-400', unknown: 'text-ocean-400',
  }
  return (
    <section>
      <button
        onClick={() => setExpanded(e => !e)}
        className="flex items-center gap-2 mb-3 w-full text-left"
      >
        <History className="w-4 h-4 text-ocean-500" />
        <h2 className="font-display font-bold text-base text-ocean-300">Alert History (7 days)</h2>
        <span className="text-ocean-600 text-xs">{data.length} past alerts</span>
        <span className="ml-auto text-ocean-600">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </span>
      </button>
      {expanded && (
        <div className="space-y-2">
          {data.map(entry => (
            <div key={entry.id} className="card opacity-70 border-l-2 border-ocean-700 py-2 px-3">
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold uppercase ${severityColor[entry.severity] ?? severityColor.unknown}`}>
                  {entry.alert_type}
                </span>
                <p className="text-ocean-200 text-xs flex-1 leading-snug">{entry.headline}</p>
              </div>
              <p className="text-ocean-600 text-xs mt-1">{timeAgo(entry.first_seen_at)}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

export default function App() {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [activeTab, setActiveTab] = useState<NavTab>(() => {
    const saved = localStorage.getItem('active-tab') as NavTab | null
    return saved ?? 'alerts'
  })

  const handleTabChange = (tab: NavTab) => {
    setActiveTab(tab)
    localStorage.setItem('active-tab', tab)
  }
  const [showMap, setShowMap] = useState(false)
  const [showSirens, setShowSirens] = useState(false)
  const [forecastCity, setForecastCity] = useState<ForecastCityKey>('kahului')
  const [page, setPage] = useState<'home' | 'admin'>(() =>
    window.location.hash === '#admin' ? 'admin' : 'home'
  )

  // Hash-based routing (no React Router needed)
  useEffect(() => {
    const onHash = () => setPage(window.location.hash === '#admin' ? 'admin' : 'home')
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  // Saved routes — sync with backend whenever they change
  const { saved: savedRoutes, isSaved, toggle: toggleSaved } = useSavedRoutes()

  useEffect(() => {
    syncSavedRoutes([...savedRoutes])
  }, [savedRoutes])

  // Data fetching
  const roads = useApi(getRoadClosures)
  const weatherFetcher = useCallback(() => getWeather(forecastCity), [forecastCity])
  const weather = useApi(weatherFetcher)
  const quakes = useApi(getEarthquakes)
  const volcanic = useApi(getVolcanic)
  const surf = useApi(getSurf)
  const community = useApi(getCommunityAlerts)
  const tsunami = useApi(getTsunami)
  const aqi = useApi(getAQI)
  const alertHistory = useApi(getAlertHistory)

  // Refresh all data
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true)
    await Promise.all([
      roads.refresh(), weather.refresh(), quakes.refresh(),
      volcanic.refresh(), surf.refresh(), community.refresh(),
      tsunami.refresh(), aqi.refresh(), alertHistory.refresh(),
    ])
    setIsRefreshing(false)
  }, [roads, weather, quakes, volcanic, surf, community, tsunami, aqi, alertHistory])

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      roads.refresh()
      weather.refresh()
      quakes.refresh()
      volcanic.refresh()
      surf.refresh()
      community.refresh()
      tsunami.refresh()
      aqi.refresh()
      alertHistory.refresh()
    }, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [
    roads.refresh, weather.refresh, quakes.refresh, volcanic.refresh,
    surf.refresh, community.refresh, tsunami.refresh, aqi.refresh, alertHistory.refresh,
  ])

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

  const alertCount = weather.data?.alerts?.length ?? 0
  const tsunamiCount = tsunami.data?.alerts?.length ?? 0
  const totalAlertBadge = tsunamiCount + alertCount + (community.data?.alerts?.length ?? 0)

  if (page === 'admin') return <AdminPage />

  const communityAlerts: CommunityAlert[] = community.data?.alerts ?? []
  const roadsList = roads.data?.roads ?? []

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

      {/* Bottom nav */}
      <BottomNav active={activeTab} onChange={handleTabChange} alertBadge={totalAlertBadge} />

      {/* Extra bottom padding so content doesn't hide behind nav bar */}
      <main className="max-w-4xl mx-auto px-4 py-6 pb-24 space-y-8">

        {/* ============================================= */}
        {/* ALERTS TAB                                    */}
        {/* ============================================= */}
        {activeTab === 'alerts' && <>
          {tsunamiCount > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <TriangleAlert className="w-5 h-5 text-red-400" />
                <h2 className="font-display font-bold text-lg">Tsunami Alerts</h2>
                <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-0.5 rounded-full animate-pulse">
                  {tsunamiCount} ACTIVE
                </span>
              </div>
              <div className="space-y-3">
                {tsunami.data!.alerts.map((alert, idx) => (
                  <TsunamiCard key={alert.id ?? idx} alert={alert} />
                ))}
              </div>
            </section>
          )}

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

          <section>
            <div className="flex items-center gap-2 mb-4">
              <CloudLightning className="w-5 h-5 text-lava-400" />
              <h2 className="font-display font-bold text-lg">Weather Alerts</h2>
              {alertCount > 0 && (
                <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-0.5 rounded-full">
                  {alertCount} active
                </span>
              )}
              {weather.data?.last_updated && (
                <span className={`ml-auto text-xs flex items-center gap-1 ${isStale(weather.data.last_updated) ? 'text-amber-400' : 'text-ocean-600'}`}>
                  {isStale(weather.data.last_updated) && <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse inline-block" />}
                  {timeAgo(weather.data.last_updated)}
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
                <p className="text-green-400 text-sm text-center py-2">No active weather alerts for Maui. All clear!</p>
              </div>
            )}
          </section>

          <AlertHistorySection data={alertHistory.data?.alerts ?? []} />
        </>}

        {/* ============================================= */}
        {/* ROADS TAB                                     */}
        {/* ============================================= */}
        {activeTab === 'roads' && <>
          <section>
            <div className="flex items-center gap-2 mb-4">
              <Route className="w-5 h-5 text-lava-400" />
              <h2 className="font-display font-bold text-lg">Road Closures</h2>
              {roads.data && roads.data.total > 0 && (
                <span className="bg-lava-500/20 text-lava-400 text-xs font-bold px-2 py-0.5 rounded-full">
                  {roads.data.total} reported
                </span>
              )}
              {roads.data?.last_scraped && (
                <span className={`ml-auto text-xs flex items-center gap-1 ${isStale(roads.data.last_scraped) ? 'text-amber-400' : 'text-ocean-600'}`}>
                  {isStale(roads.data.last_scraped) && <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse inline-block" />}
                  {timeAgo(roads.data.last_scraped)}
                </span>
              )}
            </div>
            {roads.loading ? (
              <LoadingSpinner message="Checking road conditions..." />
            ) : roads.error ? (
              <ErrorMessage message={roads.error} onRetry={roads.refresh} />
            ) : roadsList.length > 0 ? (
              <div className="space-y-3">
                {roadsList.map((road, idx) => (
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

          <section>
            <div className="flex items-center gap-2 mb-4">
              <Map className="w-5 h-5 text-ocean-400" />
              <h2 className="font-display font-bold text-lg">Maui Map</h2>
              <button
                onClick={() => setShowMap(m => !m)}
                className="ml-auto text-xs text-ocean-400 hover:text-ocean-200 transition-colors"
              >
                {showMap ? 'Hide map' : 'Show map'}
              </button>
            </div>
            {showMap && (
              <>
                <div className="flex items-center gap-3 mb-3">
                  <button
                    onClick={() => setShowSirens(s => !s)}
                    className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-xl border transition-colors ${
                      showSirens
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                        : 'bg-white/[0.05] text-ocean-500 border-white/[0.07] hover:bg-white/[0.10]'
                    }`}
                  >
                    📢 {showSirens ? 'Hide sirens' : 'Show tsunami sirens'}
                  </button>
                  <span className="text-ocean-600 text-xs">Siren locations are approximate</span>
                </div>
                <MapView roads={roadsList} showSirens={showSirens} />
              </>
            )}
          </section>
        </>}

        {/* ============================================= */}
        {/* WEATHER TAB                                   */}
        {/* ============================================= */}
        {activeTab === 'weather' && <>
          <section>
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="w-5 h-5 text-ocean-400" />
              <h2 className="font-display font-bold text-lg">Forecast</h2>
            </div>
            <div className="flex gap-1.5 mb-4 overflow-x-auto pb-1 -mx-1 px-1">
              {(Object.entries(FORECAST_CITIES) as [ForecastCityKey, string][]).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setForecastCity(key)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-colors flex-shrink-0 ${
                    forecastCity === key
                      ? 'bg-ocean-500 text-white'
                      : 'bg-white/[0.05] text-ocean-400 hover:bg-white/[0.10] border border-white/[0.07]'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            {weather.loading ? (
              <LoadingSpinner message={`Checking forecast for ${FORECAST_CITIES[forecastCity]}...`} />
            ) : weather.data?.forecasts && weather.data.forecasts.length > 0 ? (
              <ForecastBar forecasts={weather.data.forecasts} />
            ) : null}
          </section>

          {aqi.data && aqi.data.readings.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Wind className="w-5 h-5 text-cyan-400" />
                <h2 className="font-display font-bold text-lg">Air Quality</h2>
                {aqi.data.is_vog_advisory && (
                  <span className="bg-orange-500/20 text-orange-400 text-xs font-bold px-2 py-0.5 rounded-full">
                    Vog Advisory
                  </span>
                )}
                <span className="text-ocean-500 text-xs ml-1">EPA AirNow</span>
              </div>
              <AirQualityCard data={aqi.data} />
            </section>
          )}
        </>}

        {/* ============================================= */}
        {/* ACTIVITY TAB                                  */}
        {/* ============================================= */}
        {activeTab === 'activity' && <>
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
                <p className="text-ocean-400 text-sm text-center py-2">No earthquakes above M2.5 near Hawaii recently.</p>
              </div>
            )}
          </section>

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

          {surf.data?.spots && surf.data.spots.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Waves className="w-5 h-5 text-ocean-400" />
                <h2 className="font-display font-bold text-lg">Surf Report</h2>
                <span className="text-ocean-500 text-xs ml-1">NOAA buoy data</span>
                {timeAgo(surf.data.last_updated) && (
                  <span className="ml-auto text-ocean-600 text-xs">{timeAgo(surf.data.last_updated)}</span>
                )}
              </div>
              <div className="space-y-3">
                {surf.data.spots.map(spot => (
                  <SurfCard key={spot.buoy_id} spot={spot} />
                ))}
              </div>
            </section>
          )}
        </>}

        {/* ============================================= */}
        {/* PREP TAB                                      */}
        {/* ============================================= */}
        {activeTab === 'prep' && <ChecklistSection />}

        {/* Footer — shown on all tabs */}
        <footer className="text-center text-ocean-500 text-xs py-4 border-t border-ocean-800">
          <p>Maui Alert Hub v0.2.0</p>
          <p className="mt-1">Data from NWS, USGS, NOAA, EPA AirNow, and Maui County. Not an official government source.</p>
        </footer>
      </main>
    </div>
  )
}
