# 🌊 Maui Alert Hub

**Real-time road closures, weather alerts, and emergency info for Maui residents.**

No more checking five different county websites. One app. Everything you need to get around Maui safely.

## Why This Exists

Living on Maui means dealing with:
- Road closures that change daily (especially Hana Highway)
- Flash flood warnings with zero notice
- Storm damage that cuts off entire communities
- Scattered, hard-to-find county updates

Maui Alert Hub puts it all in one place, optimized for your phone, with push notifications when your routes are affected.

## Features (MVP)

- **Road Dashboard:** Real-time road closures and conditions across Maui
- **Weather Alerts:** NWS watches, warnings, and forecasts for Maui County
- **Storm Prep:** Personalized checklist to track your emergency supplies
- **Notifications:** Get alerted when roads on your saved routes close

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | SQLite (dev), PostgreSQL (prod) |
| Data Sources | Maui County site, NWS API, Hawaii DOT |

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`
API runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

## Project Roadmap

- [x] Project scaffold and CLAUDE.md
- [ ] Phase 1: Road closures dashboard + NWS weather alerts
- [ ] Phase 2: Push notifications + saved routes
- [ ] Phase 3: Storm prep checklist with offline support
- [ ] Phase 4: Community reports + mutual aid features
- [ ] Phase 5: Mobile app (React Native)

## Contributing

Built by Sam from Maui. Open to contributions from fellow island residents who want to make this better for our community.

## License

MIT
