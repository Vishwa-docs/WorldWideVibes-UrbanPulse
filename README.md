# UrbanPulse

**AI-Powered Workforce & Economic Opportunity Copilot for Montgomery, Alabama**

> Built for the World Wide Vibes GenAI.Works Hackathon — March 2026

**Live Demo**: [urbanpulse-api-production.up.railway.app](https://urbanpulse-api-production.up.railway.app) | **Repo**: [github.com/Vishwa-docs/WorldWideVibes-UrbanPulse](https://github.com/Vishwa-docs/WorldWideVibes-UrbanPulse)

---

## The Problem

Montgomery, Alabama faces deep structural economic challenges that open data alone cannot solve:

| Indicator | Value | Source |
|-----------|-------|--------|
| Population | 200,603 | U.S. Census 2020 |
| Poverty rate | **19.7%** (nearly 1 in 5 residents) | ACS 2023 |
| Median household income | $57,300 (below national $75,149) | ACS 2023 |
| Total housing units | 93,920 | Census 2020 |
| Unemployment rate | 2.7% | ACS 2023 |
| Median rent | $1,023 | ACS 2023 |

The city publishes **60+ datasets** through its ArcGIS open data portal — business licenses, 311 service requests, foot traffic, code violations, building permits, and more. Yet:

- **No tool exists** to cross-reference business licenses with foot traffic to reveal demand-supply gaps.
- **Vacant and blighted properties** are tracked across multiple disconnected systems (311 reports, code enforcement, property records) with no unified view.
- **City-owned surplus parcels** sit idle because economic development staff lack data-driven prioritization tools.
- **Entrepreneurs** have no way to identify underserved neighborhoods with high foot traffic but few businesses — the exact locations where new ventures would have the greatest impact.
- **Residents and jobseekers** cannot see where job growth concentrates or which training programs align with local hiring demand.

**The gap is not data — it's intelligence.** Montgomery's open data is rich but fragmented. UrbanPulse fuses it with web signals, federal demographics, and AI reasoning to deliver **actionable, role-specific recommendations** that turn raw data into clear next steps for residents, entrepreneurs, city staff, and educators.

---

## Our Solution

UrbanPulse is a civic-intelligence platform that combines **Montgomery Open Data (8 ArcGIS endpoints)**, **Bright Data web signals (4 products)**, **US Census ACS (31 variables)**, **Open-Meteo weather**, and **Azure OpenAI (GPT-4o-2)** into role-specific, evidence-backed economic opportunity recommendations.

Every data source is **live and real** — all 8 ArcGIS endpoints return actual Montgomery data with zero mock or simulated fallbacks.

---

## Challenge Track

**Workforce, Business & Economic Growth**

| Requirement | How UrbanPulse Delivers |
|-------------|------------------------|
| City of Montgomery Open Data | **8 ArcGIS REST APIs** — 311 requests, business licenses, foot traffic, visitor origin, code violations, opportunity zones, city-owned properties, building permits — **all live data** |
| Bright Data Integration | **4 products**: Web Scraper, SERP API, Web Unlocker, MCP Server |
| AI / GenAI | Azure OpenAI (GPT-4o-2) multi-role recommendation engine with evidence contracts |
| Social Impact | Equity-weighted scoring, service-gap analysis, underserved-area prioritization |
| Commercial Potential | City-agnostic architecture, SaaS $2K–15K/mo per city ([business model](docs/business-model.md)), **in-app Business Model page** at `/business` |

### Challenge Problems Addressed

| Challenge Brief Problem | How UrbanPulse Solves It |
|------------------------|--------------------------|
| "Compare business licenses with foot traffic trends" | Cross-references business license data with Most Visited Locations + Visitor Origin. Radar chart overlays licenses vs foot traffic. |
| "Identify and address vacant properties" | Surfaces vacant/blighted parcels from 311 reports + code violations + property data, scores each for redevelopment potential. |
| "Analyze and improve usage of city-owned properties" | Highlights surplus and city-owned parcels with opportunity scores and equity weighting via dedicated ArcGIS layer. |

---

## Features

### Opportunity Copilot (Landing Page)
- **4 Role-Based Lenses** — Resident, Entrepreneur, City Staff, Education — each with tuned scoring weights
- **Scenario selector** — General, Grocery, Clinic, Daycare, Coworking — changes scoring weights per use-case
- **Multi-objective scoring** — Resident Fit, Business Opportunity, City Impact, and composite overall ranking
- **Auto-loaded property recommendations** — top-scoring properties load automatically per role and scenario
- **Data Sources & Trust sidebar** — source-level traceability showing type, freshness, confidence, and live/cached status
- **Signal change feed** — delta engine tracks shifts in activity index over 48-hour windows

### Site Selection Workspace
- **Interactive Leaflet map** with property markers and **14 toggleable data layers**
- **Montgomery ArcGIS overlays** — 311 requests, business licenses, foot traffic, vacant reports, code violations, opportunity zones, city-owned parcels, building permits
- **Property scorecards** — detailed scoring breakdowns on click
- **AI Agent Chat** — collapsible copilot for natural-language questions about properties and opportunities
- **Collapsible Map Layers panel** — toggleable data layer controls
- **Watchlist & compare** — save properties and side-by-side comparison
- **CSV export** for operational workflows

### City Insights & Analytics
- **Interactive recharts dashboard** — business licenses by type, foot traffic hotspots, 311 requests by category, property score distribution, workforce industry breakdown, property types breakdown
- **Radar chart** comparing business licenses vs foot traffic (directly addresses challenge)
- **Web Intelligence panel** — SERP search for Montgomery business landscape, URL scraper, Bright Data capabilities view
- **Weather widget** — real-time current conditions + 7-day forecast via Open-Meteo
- **Enhanced demographics** from Census ACS (31 variables: education, commuting, transportation), workforce data, market gap analysis

### Business Model & Commercial Pitch
- **In-app `/business` page** — pricing tiers, market sizing, competitive landscape, 3-year revenue projections, unit economics, go-to-market strategy rendered as a polished UI page
- Detailed [docs/business-model.md](docs/business-model.md) with full numbers

### Data Integrity
- **100% live data** — all 8 ArcGIS endpoints return real Montgomery data; no mock or simulated fallbacks
- **Provenance metadata** — every data point carries source type, freshness timestamp, and confidence score
- **Graceful degradation** — if an ArcGIS endpoint is unreachable, the app logs a warning and returns an empty set (no fake data injected)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + TypeScript 5.9 + Vite 7.3 + Tailwind CSS v4 |
| Charts | Recharts 3.x |
| Mapping | Leaflet + react-leaflet |
| Backend | Python 3.11 / FastAPI |
| Database | SQLite via SQLModel/SQLAlchemy |
| AI/LLM | Azure OpenAI GPT-4o-2 (with deterministic fallback) |
| Web Data | Bright Data (4 products — Web Scraper, SERP API, Web Unlocker, MCP Server) |
| City Data | Montgomery ArcGIS REST (8 endpoints, open, no auth) |
| Weather | Open-Meteo API (free, no key) |
| Demographics | US Census ACS API (31 variables) |
| Places | Google Places API |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your API keys
python -m scripts.seed_sample
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (or the port Vite assigns).

| Route | View |
|-------|------|
| `/` | Opportunity Copilot |
| `/site` | Site Selection Map |
| `/compare` | Property Comparison |
| `/story` | Story Mode |
| `/insights` | City Insights & Analytics |
| `/business` | Business Model & Commercial Pitch |

### Environment Variables (Backend `.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Optional | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_KEY` | Optional | Azure OpenAI key |
| `AZURE_OPENAI_DEPLOYMENT` | Optional | Deployment name (e.g. gpt-4o-2) |
| `AZURE_OPENAI_API_VERSION` | Optional | API version |
| `BRIGHTDATA_API_TOKEN` | Optional | Bright Data API token |
| `BRIGHTDATA_SERP_ZONE` | Optional | SERP API zone name |
| `BRIGHTDATA_UNLOCKER_ZONE` | Optional | Web Unlocker zone name |
| `GOOGLE_PLACES_API_KEY` | Optional | Google Places key |
| `CENSUS_API_KEY` | Optional | US Census ACS key |
| `DATABASE_URL` | No | SQLite (defaults to local file) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |

> **All keys are optional** — the app runs in fallback mode without them. Azure OpenAI falls back to template-based responses. Bright Data uses simulated signals. ArcGIS, Census, and Weather endpoints are free and require no keys.

---

## Data Sources

| Source | Type | Auth | Usage |
|--------|------|------|-------|
| [Montgomery ArcGIS Portal](https://mgmgis.montgomeryal.gov) | City Open Data | None (public) | 311 requests, business licenses, foot traffic, vacant reports, code violations, opportunity zones, city-owned properties, building permits |
| [Open-Meteo](https://open-meteo.com) | Weather API | None (free) | Current conditions, 7-day forecast for Montgomery |
| [Bright Data](https://brightdata.com) | Web Intelligence | API Token | POI scraping, SERP search, page scraping, MCP agent access |
| [US Census ACS](https://api.census.gov) | Federal Demographics | API Key | 31 workforce/demographic variables — population, income, education, commuting, transportation |
| [Google Places](https://developers.google.com/maps/documentation/places) | Places API | API Key | Walk score computation, nearby amenities |

---

## Hackathon Judging Alignment

**Total: 35 points**

| Criterion | Max | How UrbanPulse Addresses It |
|-----------|-----|---------------------------|
| **Relevance to Challenge** | 10 | 3+ challenge problems addressed: business licenses vs foot traffic, vacant properties, city-owned property analysis, 311 service requests, code violations, opportunity zones. **8 ArcGIS endpoints** (all live) + Census (31 vars) + Weather + Bright Data (4 products). |
| **Quality & Design** | 10 | Professional dark-gradient UI, 4-role architecture, 7 recharts analytics visualizations, **14-layer interactive map**, AI Agent Chat, 137 tests passing, 0 TS errors, clean production build. |
| **Originality** | 5 | No existing civic AI copilot for site selection. Equity-weighted scoring surfaces underserved areas first. Radar chart overlaying business licenses vs foot traffic. Multi-role persona system with scenario-specific weights. |
| **Social Impact** | 5 | Equity-first scoring surfaces food deserts, vacant parcels, and underserved neighborhoods. Four stakeholder lenses ensure broad community benefit. Directly addresses Montgomery's 19.7% poverty rate and economic disinvestment. |
| **Commercial Potential** | 5 | SaaS tiers: Starter $2K/mo, Pro $5K/mo, Enterprise $10K–15K/mo — **undercuts Esri Hub ($25K+/yr) and mySidewalk ($12K+/yr)** while adding AI + web signals. 85% gross margin (public data = free COGS). City-agnostic config-driven architecture — new city onboards in < 1 week. TAM: 19,500+ US municipalities, $105B muni IT market. See [business model](docs/business-model.md). |

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings management
│   │   ├── database.py          # SQLite setup
│   │   ├── models/              # SQLModel schemas
│   │   ├── routes/              # API endpoints (16 routers)
│   │   └── services/            # Business logic
│   │       ├── scoring.py       # Multi-objective scoring engine
│   │       ├── opportunity_engine.py  # Role-based recommendations
│   │       ├── brightdata_client.py   # Bright Data (4 products)
│   │       ├── arcgis_service.py      # Montgomery ArcGIS data (8 endpoints, 100% live)
│   │       ├── weather_service.py     # Open-Meteo weather integration
│   │       ├── llm_service.py         # Azure OpenAI + fallback
│   │       ├── signals_service.py     # Signal delta tracking
│   │       └── agents/               # AI agents (orchestrator + 3 specialists)
│   ├── scripts/                 # Data ingestion & seeding
│   ├── tests/                   # 137 tests
│   └── data/raw/               # Raw data files
├── frontend/
│   └── src/
│       ├── components/          # React components
│       │   ├── Insights/        # AnalyticsCharts, WebIntelligence, Weather, Demographics
│       │   ├── Agent/           # AI copilot chat (Site Workspace)
│       │   └── Map/             # LayerControls (14-layer toggle)
│       ├── pages/               # Copilot, Dashboard, Compare, Story, Insights, BusinessModel
│       ├── services/api.ts      # Typed API client
│       └── types/index.ts       # TypeScript interfaces
├── docs/                        # Documentation & demo scripts
├── sample_prompts/              # Hackathon sample prompts
└── config/cities/               # City configurations
```

---

## Testing

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v   # 137 tests

cd ../frontend
npm run build                # TypeScript + production build check
```

---

## Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Full App | Railway | [urbanpulse-api-production.up.railway.app](https://urbanpulse-api-production.up.railway.app) |

The app is deployed as a **single unified service** — the Dockerfile builds the React frontend and serves it from FastAPI alongside the API. No separate frontend hosting required.

See [docs/deploy-free.md](docs/deploy-free.md) for full deployment instructions.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, data flow, scoring engine |
| [Data Sources](docs/data-sources.md) | All data sources with endpoints and schemas |
| [API Reference](docs/api.md) | Full REST API documentation |
| [Setup Guide](docs/setup.md) | Installation, configuration, troubleshooting |
| [Deploy](docs/deploy-free.md) | Free-tier deployment guide |
| [Demo Script](docs/demo-video.md) | Demo recording script and walkthrough |
| [Business Model](docs/business-model.md) | Pricing, unit economics, revenue projections, go-to-market |
| [Submission Brief](docs/submission-brief.md) | Hackathon submission summary |

---

## License

MIT — Built for the World Wide Vibes GenAI.Works Hackathon
