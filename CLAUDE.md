# Maui Alert Hub - Claude Code Instructions

## Project Overview

**Maui Alert Hub** is a hyperlocal web app for Maui, Hawaii residents that aggregates real-time road closures, weather alerts, storm prep info, and community updates into one clean, mobile-first dashboard. The goal is to replace the scattered, clunky county websites and give residents a single source of truth for daily life on Maui.

## Tech Stack

- **Frontend:** React 18 + Vite + TypeScript + Tailwind CSS
- **Backend:** Python FastAPI
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Scraping:** BeautifulSoup4 + httpx for county data
- **Weather API:** National Weather Service (NWS) free API
- **Deployment:** Vercel (frontend) + Railway or Render (backend)

## Project Structure

```
maui-alert-hub/
├── CLAUDE.md              # You are here
├── README.md              # Project docs
├── frontend/              # React + Vite app
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page-level components
│   │   ├── utils/         # Helper functions
│   │   └── assets/        # Images, icons, fonts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.js
├── backend/               # FastAPI Python backend
│   ├── app/
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── api/           # API route handlers
│   │   ├── scrapers/      # Web scrapers for county data
│   │   ├── models/        # Data models (Pydantic)
│   │   └── services/      # Business logic layer
│   ├── tests/             # Pytest test files
│   ├── requirements.txt
│   └── .env.example
└── docs/                  # Design docs, API specs
    └── MVP_SPEC.md
```

## Coding Standards

### Python (Backend)
- PEP 8 with Black formatting, 4 spaces indentation
- Detailed docstrings for all functions
- Type hints on all function signatures
- Use `py` command on Windows (Sam's local machine)
- 4x4 debug logging: log inputs, outputs, timing, and status for every function
- Use decorators for logging where possible
- Comprehensive error handling with try/except blocks

### TypeScript/React (Frontend)
- 2 spaces indentation
- Functional components with hooks only (no class components)
- Props interfaces defined above each component
- Use Tailwind CSS utility classes (no separate CSS files)
- Mobile-first responsive design

### General Rules
- NO em dashes in any text content (use commas, periods, or parentheses)
- All commits should be descriptive and follow conventional commits
- Every new feature needs at least one test
- Keep components small and focused (under 150 lines)
- Use environment variables for all API keys and config

## Data Sources

1. **Maui County Website** (mauicounty.gov) - Road closures, emergency alerts
2. **NWS API** (api.weather.gov) - Weather forecasts, flood/storm watches for Maui
3. **Hawaii DOT** - Highway conditions and construction updates
4. **USGS** - Earthquake and volcanic activity (Haleakala monitoring)

## MVP Features (Phase 1)

1. **Road Status Dashboard** - Real-time road closures and conditions
2. **Weather Alerts** - NWS watches, warnings, advisories for Maui
3. **Storm Prep Checklist** - Personalized supply tracker
4. **Push Notifications** - Alerts when your saved routes are affected

## Design Direction

- **Theme:** Island-modern, clean, accessible
- **Colors:** Ocean blues + volcanic earth tones + alert reds/oranges
- **Mobile-first:** 80%+ of Maui residents will use this on their phones
- **Accessibility:** WCAG 2.1 AA minimum (large text, high contrast)
- **Dark mode:** Essential for nighttime storm tracking
- **Offline support:** Basic cached data for when connectivity drops (common in rural Maui)

## Environment Variables

### Backend (.env)
```
NWS_USER_AGENT=MauiAlertHub/1.0 (contact@mauialerthub.com)
DATABASE_URL=sqlite:///./maui_alert_hub.db
SCRAPE_INTERVAL_MINUTES=5
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:5173
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Maui Alert Hub
```

## Commands

### Backend
```bash
cd backend
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload --port 8000
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm install
npm run dev
npm run build
npm run lint
```

## Key Decisions Log

- **Why React + FastAPI (not Next.js)?** Sam has existing experience with both React (CS290) and Python/FastAPI. Keeping frontend and backend separate also makes deployment and scaling simpler for an MVP.
- **Why SQLite for dev?** Zero setup. Switch to PostgreSQL for production via environment variable.
- **Why scraping instead of official APIs?** Maui County doesn't have a public API. We scrape responsibly with rate limiting and caching.
- **Why NWS API?** Free, reliable, no API key needed (just a User-Agent header). Perfect for MVP budget.
