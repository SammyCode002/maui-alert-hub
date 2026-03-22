/**
 * Interactive map of Maui showing road closures and tsunami siren locations.
 *
 * Uses React Leaflet + OpenStreetMap tiles (no API key needed).
 * Road pins are color-coded by status (red=closed, amber=restricted, green=open).
 * Siren pins show civil defense warning siren locations.
 */

import { MapContainer, TileLayer, CircleMarker, Popup, Marker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { RoadClosure } from '../utils/types'

// Fix Leaflet's default icon path issue with Vite bundling
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// Custom siren icon using a div
const sirenIcon = L.divIcon({
  className: '',
  html: `<div style="
    width:20px;height:20px;border-radius:50%;
    background:rgba(251,191,36,0.9);
    border:2px solid rgba(251,191,36,1);
    box-shadow:0 0 8px rgba(251,191,36,0.6);
    display:flex;align-items:center;justify-content:center;
    font-size:10px;line-height:1;
  ">📢</div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
})

// Maui tsunami warning siren locations (approximate, based on civil defense zones)
const SIREN_LOCATIONS: Array<{ lat: number; lon: number; name: string }> = [
  { lat: 20.8985, lon: -156.4700, name: 'Kahului Harbor' },
  { lat: 20.8950, lon: -156.4776, name: 'Kahului Beach' },
  { lat: 20.9140, lon: -156.3594, name: 'Paia' },
  { lat: 20.7580, lon: -156.4418, name: 'Kihei' },
  { lat: 20.7924, lon: -156.5059, name: 'Maalaea' },
  { lat: 20.8758, lon: -156.6820, name: 'Lahaina' },
  { lat: 20.9213, lon: -156.6943, name: 'Kaanapali' },
  { lat: 21.0050, lon: -156.6671, name: 'Kapalua' },
  { lat: 20.7579, lon: -155.9892, name: 'Hana' },
  { lat: 20.6803, lon: -156.4415, name: 'Wailea' },
  { lat: 20.6408, lon: -156.4420, name: 'Makena' },
  { lat: 20.8900, lon: -156.5027, name: 'Wailuku' },
]

const statusColors: Record<string, string> = {
  closed:     '#dc2626',
  restricted: '#d97706',
  open:       '#16a34a',
  unknown:    '#6b7280',
}

interface MapViewProps {
  roads: RoadClosure[]
  showSirens: boolean
}

// Road closures don't have lat/lon in our data, so we show a legend instead
// and use approximate positions for known Maui roads
const ROAD_COORDS: Record<string, [number, number]> = {
  'hana highway':        [20.8800, -156.2500],
  'piilani highway':     [20.7200, -156.3900],
  'honoapiilani highway':[20.8400, -156.5900],
  'kahekili highway':    [20.9600, -156.6200],
  'crater road':         [20.7100, -156.2500],
  'haleakala highway':   [20.8200, -156.3300],
  'kokomo road':         [20.8600, -156.3300],
  'baldwin avenue':      [20.9000, -156.3800],
}

function getRoadCoords(roadName: string): [number, number] | null {
  const lower = roadName.toLowerCase()
  for (const [key, coords] of Object.entries(ROAD_COORDS)) {
    if (lower.includes(key)) return coords
  }
  return null
}

export default function MapView({ roads, showSirens }: MapViewProps) {
  const mappableRoads = roads
    .map(r => ({ road: r, coords: getRoadCoords(r.road_name) }))
    .filter(({ coords }) => coords !== null) as Array<{ road: RoadClosure; coords: [number, number] }>

  return (
    <div className="rounded-2xl overflow-hidden border border-white/[0.09]" style={{ height: '340px' }}>
      <MapContainer
        center={[20.8000, -156.3500]}
        zoom={10}
        style={{ height: '100%', width: '100%', background: '#0b1f33' }}
        zoomControl={true}
        scrollWheelZoom={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com">CARTO</a>'
        />

        {/* Road closure markers */}
        {mappableRoads.map(({ road, coords }) => (
          <CircleMarker
            key={road.id ?? road.road_name}
            center={coords}
            radius={8}
            pathOptions={{
              color: statusColors[road.status] ?? statusColors.unknown,
              fillColor: statusColors[road.status] ?? statusColors.unknown,
              fillOpacity: 0.85,
              weight: 2,
            }}
          >
            <Popup>
              <div className="text-sm font-semibold">{road.road_name}</div>
              <div className="text-xs capitalize" style={{ color: statusColors[road.status] }}>
                {road.status}
              </div>
              {road.location && <div className="text-xs text-gray-400 mt-1">{road.location}</div>}
            </Popup>
          </CircleMarker>
        ))}

        {/* Tsunami siren markers */}
        {showSirens && SIREN_LOCATIONS.map(siren => (
          <Marker
            key={siren.name}
            position={[siren.lat, siren.lon]}
            icon={sirenIcon}
          >
            <Popup>
              <div className="text-sm font-semibold">Civil Defense Siren</div>
              <div className="text-xs text-gray-400">{siren.name}</div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}
