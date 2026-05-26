<h1 align="center">
  🌊 Maui Alert Hub
</h1>
<p align="center">
  <strong>Real-time hyperlocal alerts for Maui residents.</strong>
</p>
<p align="center">
  Road closures, NWS weather, USGS earthquakes, NOAA surf, tsunami warnings, EPA air quality, and Haleakalā volcanic activity, all in one mobile-first PWA. Push notifications fire when a saved route is affected.
</p>
<p align="center">
  <a href="https://maui-alert-hub.vercel.app" target="_blank"><strong>Live site →</strong></a>
</p>

## why this exists

Living on Maui means juggling five different county and federal websites just to figure out if Hāna Highway is open, whether a flash flood watch is in effect, or if a swell is dangerous. Each agency publishes data differently. Some sources go down. Some are buried in PDFs.

Maui Alert Hub aggregates the official data sources into one clean dashboard, refreshes every few minutes in the background, and pushes notifications when something on a route you care about changes.

## features

- **Road closures dashboard** with descriptions and severity badges, sorted with daily-use content first
- **NWS weather** including watches, warnings, multi-day forecasts, and per-city Maui coverage
- **USGS earthquakes** with magnitude, depth, and proximity to Maui
- **NOAA surf and buoy data** with wave height and direction
- **Tsunami warnings** integrated with NTWC alerts
- **EPA Air Quality + vog** levels for Maui County
- **Haleakalā volcanic activity** via USGS HANS public API
- **Interactive map** showing alert locations and severity
- **Saved routes** with push notifications when affected
- **PWA install banner** with Android and iOS support
- **Web Push notifications** via VAPID
- **Bottom navigation** with 5 tabs (Roads, Weather, Map, Prep, Settings)
- **Storm prep checklist** with personalized supply tracking
- **Tab memory and history** for quick return-to-where-you-were
- **Share button** to send alerts to family and neighbors
- **Stale-data indicators** when scrapers fail or sources go down
- **Dark mode** for nighttime storm tracking
- **Offline-aware** with cached data for rural connectivity dropouts

## tech stack

| Layer | Tech |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | Python 3.10+, FastAPI, SQLAlchemy (async) |
| Database | PostgreSQL (prod), SQLite (dev) |
| Caching | APScheduler background tasks, in-memory caching |
| Notifications | Web Push (pywebpush, VAPID) |
| Rate Limiting | slowapi |
| Analytics | Vercel Web Analytics |
| PWA | Service Worker (sw.ts), Web App Manifest |
| Deployment | Vercel (frontend), Render (backend) |
| Monitoring | UptimeRobot (health checks via HEAD endpoint) |

## data sources

| Source | Used For |
|---|---|
| Maui County website | Road closures and emergency alerts |
| Hawaii DOT | Highway conditions and construction |
| NWS API (api.weather.gov) | Weather forecasts, watches, warnings |
| USGS Earthquake API | Real-time earthquake data |
| USGS HANS | Haleakalā volcanic activity |
| NOAA buoy stations | Surf height and conditions |
| NTWC | Tsunami warnings |
| EPA AirNow | Air quality and vog levels |

## getting started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Git
- PostgreSQL (optional, SQLite works for dev)

### Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

API runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Frontend setup
```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

## environment variables

### Backend (`backend/.env`)
```
NWS_USER_AGENT=MauiAlertHub/1.0 (contact@mauialerthub.com)
DATABASE_URL=sqlite+aiosqlite:///./maui_alert_hub.db
SCRAPE_INTERVAL_MINUTES=5
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173
VAPID_PRIVATE_KEY=...
VAPID_PUBLIC_KEY=...
VAPID_CLAIM_SUB=mailto:contact@mauialerthub.com
```

### Frontend (`frontend/.env`)
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Maui Alert Hub
VITE_VAPID_PUBLIC_KEY=...
```

## architecture

```
maui-alert-hub/
├── frontend/                 React + Vite + TypeScript PWA
│   └── src/
│       ├── components/       Cards for each data source (Road, Weather, Quake, Surf, etc.)
│       ├── hooks/            Custom React hooks
│       ├── utils/            Helpers (API client, formatters, storage)
│       ├── sw.ts             Service worker for offline + push notifications
│       └── App.tsx
├── backend/                  FastAPI Python service
│   └── app/
│       ├── api/              REST endpoints
│       ├── scrapers/         One client per data source (NWS, USGS, NOAA, EPA, DOT, etc.)
│       ├── services/         Business logic (push notifications, route matching)
│       ├── models/           SQLAlchemy + Pydantic models
│       ├── database.py       Async SQLAlchemy session
│       └── main.py           FastAPI app, scheduled tasks, lifespan hooks
├── docs/                     Design docs, API specs
├── render.yaml               Render deployment config
└── README.md
```

## roadmap

- [x] **Phase 1**: Road closures dashboard, NWS weather, mobile-first PWA shell
- [x] **Phase 2**: Saved routes, push notifications, share button
- [x] **Phase 3**: Earthquakes, expandable alerts, storm prep checklist
- [x] **Phase 4**: Push notifications via VAPID, volcanic + surf data, admin panel, SEO
- [x] **Phase 5**: Tsunami alerts, AQI/vog, interactive map, multi-city forecast
- [x] **Phase 6**: Async SQLAlchemy + PostgreSQL, rate limiting, UTC timestamps
- [ ] **Phase 7**: Community reports and mutual aid features
- [ ] **Phase 8**: Native mobile app (React Native)

## contributing

Built by Sam Dameg from Maui. Open to contributions from fellow island residents who want to make this better for the community. PRs, bug reports, and feature requests welcome.

## license

MIT
