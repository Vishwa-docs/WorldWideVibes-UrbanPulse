# UrbanPulse Architecture

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
│  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ MapView  │ │ Scorecards │ │ Compare  │ │ AgentChat      │   │
│  │ (Leaflet)│ │            │ │ View     │ │ (Copilot UI)   │   │
│  └────┬─────┘ └─────┬──────┘ └────┬─────┘ └──────┬─────────┘   │
│       │              │             │               │             │
│  ┌────┴──────────────┴─────────────┴───────────────┴──────────┐  │
│  │                    API Service (axios)                      │  │
│  │                  VITE_API_BASE_URL → :8000                  │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP / JSON
┌───────────────────────────┼─────────────────────────────────────┐
│                   BACKEND (FastAPI)                              │
│  ┌────────────────────────┴───────────────────────────────────┐  │
│  │                    FastAPI Router Layer                     │  │
│  │  /api/health  /api/properties  /api/scores  /api/compare   │  │
│  │  /api/watchlist  /api/export  /api/brightdata  /api/agent  │  │
│  └──────┬─────────────┬───────────────┬───────────────┬───────┘  │
│         │             │               │               │          │
│  ┌──────┴──────┐ ┌────┴─────┐ ┌───────┴──────┐ ┌─────┴───────┐  │
│  │  Scoring    │ │ Bright   │ │  LLM Service │ │  Agent      │  │
│  │  Engine     │ │ Data     │ │  (Gemini /   │ │  Orchestr.  │  │
│  │             │ │ Client   │ │   Fallback)  │ │             │  │
│  └──────┬──────┘ └────┬─────┘ └───────┬──────┘ └──────┬──────┘  │
│         │             │               │                │         │
│  ┌──────┴─────────────┴───────────────┴────────────────┴──────┐  │
│  │                   SQLite Database (SQLModel)                │  │
│  │  properties │ property_scores │ web_signals │ incidents     │  │
│  │  service_locations │ city_projects │ watchlists             │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

         ▲                               ▲
         │  CSV / GeoJSON                │  Web Scraper API
┌────────┴────────┐             ┌────────┴────────┐
│  Montgomery     │             │   Bright Data   │
│  Open Data      │             │   (POIs,        │
│  Portal         │             │    Reviews,     │
│                 │             │    Competition) │
└─────────────────┘             └─────────────────┘
```

## Data Flow

### 1. Data Ingestion

```
Open Data Portal ──► CSV download ──► ingest_montgomery.py ──► SQLite DB
                                      (column mapping via
                                       config/cities/montgomery.json)
```

The ingestion pipeline reads CSV files from `backend/data/raw/` and maps columns
according to the city configuration file at `config/cities/montgomery.json`. This
supports three data types:

| Source File | Target Table | Description |
|---|---|---|
| `parcels.csv` | `properties` | Property parcels with zoning, coordinates, ownership |
| `incidents.csv` | `incidents` | Police/911 incidents with type, severity, location |
| `city_projects.csv` | `city_projects` | Infrastructure projects with status and budget |

For demo purposes, `scripts/seed_sample.py` generates 50 realistic Montgomery
properties, 100 incidents, 20 service locations, and 5 city projects without
requiring real CSV files.

### 2. Scoring Pipeline

```
Property ──► Gather Context ──► Compute Sub-Scores ──► Weighted Average ──► Store
               │                    │
               ├─ Nearby Services   ├─ Foot Traffic Score (0-10)
               ├─ Nearby Incidents  ├─ Competition Score (0-10)
               ├─ Web Signals       ├─ Safety Score (0-10)
               └─ Property Data     ├─ Equity Score (0-10)
                                    └─ Activity Index (0-10)
                                            │
                                    Scenario Weights ──► Overall Score (0-10)
```

### 3. API Request Flow

```
Client ──► FastAPI Router ──► Route Handler ──► Service Layer ──► Database
                                   │
                                   ├─ Scoring Engine (compute_overall_score)
                                   ├─ Bright Data Client (fetch_activity_signals)
                                   └─ Agent Orchestrator (ask_orchestrator)
```

## Agent Architecture

The AI agent system follows a **coordinator-specialist** pattern:

```
                    ┌───────────────────┐
 User Query ──────► │   Orchestrator    │ ◄──── Property Context
                    │   (Main Copilot)  │ ◄──── Score Data
                    └─────┬─────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │  Equity  │  │  Risk /  │  │   Biz    │
     │  Lens    │  │  Safety  │  │  Coach   │
     │  Agent   │  │  Lens    │  │  Agent   │
     └────┬─────┘  └────┬─────┘  └────┬─────┘
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                 ┌───────────────┐
                 │  LLM Service  │
                 │  (Gemini or   │
                 │   Fallback)   │
                 └───────────────┘
```

### Orchestrator (`services/agents/orchestrator.py`)

The main copilot that:
1. Receives a natural-language query and context (persona, scenario)
2. Fetches the top-5 ranked properties for the current scenario
3. Dispatches to specialist lens agents in parallel
4. Compiles all context into a single prompt for the LLM
5. Returns a structured response with narrative + recommended properties

### Specialist Lens Agents

| Agent | File | Focus Area |
|-------|------|-----------|
| **Equity Lens** | `agents/equity_lens.py` | Service gaps, underserved areas, community impact |
| **Risk Lens** | `agents/risk_lens.py` | Safety metrics, incident patterns, risk assessment |
| **BizCoach** | `agents/bizcoach.py` | Business viability, financial outlook, scenario-specific advice |

Each agent receives property data and scores, then generates a specialist analysis
that the Orchestrator folds into the unified response.

### LLM Abstraction (`services/llm_service.py`)

The LLM layer supports multiple providers through a common `BaseLLMService` interface:

- **`GeminiService`** — Uses Google Gemini 2.0 Flash via the `google-generativeai` SDK
- **`FallbackLLMService`** — Template-based responses when no API key is configured

This abstraction allows swapping LLM providers without touching agent or business logic.

## Bright Data Integration

```
Property Coordinates ──► BrightDataClient ──► Bright Data Web Scraper API
                                                    │
                              ┌──────────────────────┤
                              ▼                      ▼
                        fetch_pois_near       fetch_reviews_near
                              │                      │
                              └───────┬──────────────┘
                                      ▼
                            fetch_activity_signals
                                      │
                                      ▼
                            ┌─────────────────┐
                            │  WebSignal DB   │
                            │  poi_count      │
                            │  avg_rating     │
                            │  review_count   │
                            │  competitor_cnt │
                            │  activity_index │
                            └─────────────────┘
```

The `BrightDataClient` operates in two modes:

- **Live mode** (`BRIGHTDATA_API_TOKEN` configured): Calls the Bright Data Web Scraper
  API to query Google Maps for nearby businesses, reviews, and competition density.
- **Simulated mode** (no token): Returns realistic mock data seeded with deterministic
  randomness based on location coordinates, allowing full demo functionality.

Signals are cached in the `web_signals` table and can be refreshed on demand via
`POST /api/brightdata/refresh/{property_id}`.

## Scoring Engine

The scoring engine (`services/scoring.py`) evaluates properties across five dimensions,
each scored 0–10:

| Dimension | Inputs | Logic |
|---|---|---|
| **Foot Traffic** | Nearby service count, POI count, review volume | More activity = higher score |
| **Competition** | Competitor count from web signals | Fewer competitors = higher score (inverse) |
| **Safety** | Incident count/severity within 1.5 km | Fewer/less-severe incidents = higher score |
| **Equity** | Nearby services of the target type | Fewer existing services = higher need = higher score |
| **Activity Index** | POI count, ratings, review volume | Composite web-signal strength |

### Scenario-specific Weights

The **Overall Opportunity Score** is a weighted average whose weights change per scenario:

| Dimension | General | Grocery | Clinic | Daycare | Coworking |
|---|---|---|---|---|---|
| Foot Traffic | 0.25 | 0.20 | 0.15 | 0.20 | 0.30 |
| Competition | 0.20 | 0.25 | 0.15 | 0.20 | 0.20 |
| Safety | 0.20 | 0.15 | 0.20 | 0.30 | 0.15 |
| Equity | 0.20 | 0.30 | 0.35 | 0.20 | 0.10 |
| Activity | 0.15 | 0.10 | 0.15 | 0.10 | 0.25 |

For example, a **clinic** scenario heavily weights Equity (0.35) because healthcare
access gaps are the primary siting criterion, while a **coworking** scenario favors
Foot Traffic (0.30) and Activity (0.25).

## "Bring Your City" Extensibility

UrbanPulse is designed to support any city — not just Montgomery. The architecture
uses a pluggable city configuration system:

```
config/cities/
├── montgomery.json      # Currently active
├── birmingham.json      # Future: add more cities
└── mobile.json
```

Each city config file defines:

```json
{
  "city_name": "Montgomery",
  "state": "AL",
  "center": {"lat": 32.3668, "lng": -86.3000},
  "zoom": 12,
  "open_data_portal": "https://opendata.montgomeryal.gov",
  "datasets": { ... },
  "column_mapping": { ... },
  "neighborhoods": [ ... ]
}
```

To add a new city:
1. Create a JSON config with the city's center coordinates, data portal URL, dataset
   definitions, and column mappings
2. Download the city's open data CSVs into `backend/data/raw/`
3. Run the ingestion script (or create a city-specific one)
4. The scoring, agents, and UI automatically adapt to the new data

This design makes UrbanPulse commercially viable as a multi-city SaaS platform.
