# Maui Alert Hub - MVP Specification

## Problem Statement

Maui residents currently have to check multiple scattered websites (Maui County, NWS, Hawaii DOT, social media) to get basic daily information about road conditions, weather alerts, and emergency updates. During storms and emergencies, this fragmentation becomes dangerous.

## Target Users

- **Daily commuters** who need to know if their route is open (especially Hana Highway)
- **Rural residents** (Hana, Upcountry) who get cut off during storms
- **Emergency preparedness planners** tracking weather and supply readiness
- **Local businesses** that need to communicate conditions to customers/employees

## MVP Scope (Phase 1)

### Core Features

1. **Road Status Dashboard**
   - Display all current road closures and restrictions
   - Color-coded status badges (closed/restricted/open)
   - Source attribution (Maui County, DOT)
   - Last-updated timestamps

2. **Weather Alerts**
   - Active NWS watches, warnings, advisories for Maui County
   - Severity-based visual hierarchy (extreme > severe > moderate > minor)
   - Expiration times
   - Affected area descriptions

3. **Weather Forecast**
   - 7-day forecast from NWS for central Maui
   - Temperature, wind, and conditions
   - Horizontal scrollable card layout

4. **Manual Refresh**
   - One-tap refresh to pull latest data
   - Loading states during refresh

### Out of Scope (Phase 1)

- Push notifications (Phase 2)
- Saved routes / personalized alerts (Phase 2)
- Storm prep checklist (Phase 3)
- Community-submitted reports (Phase 4)
- User accounts and authentication (Phase 4)
- Native mobile app (Phase 5)
- Offline support / PWA (Phase 3)

## Data Sources

| Source | Data | Method | Rate |
|--------|------|--------|------|
| Maui County (mauicounty.gov) | Road closures | Web scraping | Every 5 min |
| NWS API (api.weather.gov) | Alerts, forecasts | REST API | On request |
| Hawaii DOT | Highway conditions | Web scraping | Every 10 min |

## Technical Architecture

```
[React Frontend] <--HTTP--> [FastAPI Backend] <---> [NWS API]
                                    |
                                    +---------> [County Scraper]
                                    |
                                    +---------> [SQLite DB]
```

## Success Metrics

- **Reliability:** App loads in under 2 seconds, data is never more than 10 minutes old
- **Adoption:** 100 Maui residents using it within first month
- **Accuracy:** Road closure data matches county announcements within 5 minutes
- **Usability:** Users can find their route status in under 3 taps

## Timeline

| Week | Milestone |
|------|-----------|
| 1 | Backend API with NWS integration working |
| 2 | County scraper parsing road closures |
| 3 | Frontend dashboard with all sections |
| 4 | Testing, polish, deploy to production |

## Risks

- **County website changes HTML structure:** Scraper breaks. Mitigation: alerting on scrape failures, fallback to cached data.
- **NWS API downtime:** Rare, but possible. Mitigation: cached last-known data with "stale" indicator.
- **Legal concerns about scraping:** We scrape responsibly (rate-limited, cached, attributed). If county objects, we work with them on an official data feed.
