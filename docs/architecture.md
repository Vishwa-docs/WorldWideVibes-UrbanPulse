# UrbanPulse Architecture

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
│  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ MapView  │ │ Scorecards │ │ Compare  │ │ AgentChat      │   │
│  │ (Leaflet)│ │ + Charts   │ │ View     │ │ (Copilot UI)   │   │
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
│  │  Engine     │ │ Data     │ │  (Azure      │ │  Orchestr.  │  │
│  │             │ │ Client   │ │   OpenAI)    │ │             │  │
│  └──────┬──────┘ └────┬─────┘ └───────┬──────┘ └──────┬──────┘  │
│         │             │               │                │         │
│  ┌──────┴─────────────┴───────────────┴────────────────┴──────┐  │
│  │                   SQLite Database (SQLModel)                │  │
│  │  properties │ property_scores │ web_signals │ incidents     │  │
│  │  service_locations │ city_projects │ watchlists             │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

         ▲                               ▲
         │  Live REST API                │  Web Scraper API
┌────────┴────────┐             ┌────────┴────────┐
│  Montgomery     │             │   Bright Data   │
│  Open Data      │             │   (POIs,        │
│  (ArcGIS REST)  │             │    Reviews,     │
│                 │             │    Competition) │
└─────────────────┘             └─────────────────┘
```

## Data Flow

### 1. Data Ingestion

```
Montgomery ArcGIS REST APIs ──► arcgis_service.py ──► Live JSON ──► SQLite DB
+ Seed script (seed_sample.py) ──► 50 demo properties if no network
```

The platform queries **eight** ArcGIS REST endpoints in real time — **all returning live data with no mock fallbacks**:

| Endpoint | Description | Source |
|---|---|---|
| `mgmgis.montgomeryal.gov/.../Received_311_Service_Request` | 311 service requests | Montgomery hosted datasets |
| `mgmgis.montgomeryal.gov/.../Business_License` | Active business licenses | Montgomery hosted datasets |
| `services7.arcgis.com/.../Most_Visited_Locations` | Foot traffic heat data | ArcGIS Online |
| `services7.arcgis.com/.../Visitors_Origin` | Visitor origin patterns | ArcGIS Online |
| `mgmgis.montgomeryal.gov/.../Code_Violations` | Code enforcement cases | Montgomery hosted datasets |
| `mgmgis.montgomeryal.gov/.../City_Owned_Properities` | City-owned parcels | Montgomery hosted datasets |
| `mgmgis.montgomeryal.gov/.../Construction_Permits` | Building permits | Montgomery hosted datasets |
| `services7.arcgis.com/.../Opportunity_Zones` | Federal tax incentive zones | ArcGIS Online |

If an ArcGIS endpoint is unreachable, the service logs a warning and returns an empty list — no simulated data is injected.

For initial setup, `scripts/seed_sample.py` generates 50 realistic Montgomery
properties, 100 incidents, 20 service locations, and 5 city projects for the
local SQLite database.

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
                 │  (Azure       │
                 │   OpenAI)     │
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

- **`AzureOpenAIService`** — Uses Azure OpenAI GPT-4o-2 (primary provider)
- **`FallbackLLMService`** — Deterministic template-based responses when no API key is configured

This abstraction allows swapping LLM providers without touching agent or business logic.

## Bright Data Integration (4 Products)

```
                           BrightDataClient
                                 │
              ┌──────────┬───────┼───────────┬──────────────┐
              ▼          ▼       ▼           ▼              ▼
        Web Scraper   SERP API  Web        MCP Server   Capabilities
        (Datasets)              Unlocker   (documented)   endpoint
              │          │       │
              ▼          ▼       ▼
        fetch_pois   search    scrape
        fetch_revs   _serp     _url
              │          │       │
              ▼          ▼       ▼
        WebSignal DB  JSON     Markdown
                     results   content
```

### Products Integrated

| # | Product | Endpoint | Purpose |
|---|---------|----------|---------|
| 1 | **Web Scraper** (Datasets API) | `POST /datasets/v3/trigger` | Google Maps POI & review data |
| 2 | **SERP API** | `POST /request` (SERP zone) | Local search engine results |
| 3 | **Web Unlocker** | `POST /request` (Unlocker zone) | Scrape any page as markdown |
| 4 | **MCP Server** | `mcp.brightdata.com/sse` | AI agent web data access |

The `BrightDataClient` operates in two modes:

- **Live mode** (`BRIGHTDATA_API_TOKEN` configured): Calls Bright Data APIs
  for real-time web data collection across all products.
- **Fallback mode** (no token): Returns deterministic placeholder data for each product,
  allowing demo functionality. All ArcGIS, Census, and Weather data remain fully
  live regardless of Bright Data configuration.

### API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/api/brightdata/signals/{id}` | GET | Web signals for a property |
| `/api/brightdata/serp` | POST | SERP API search |
| `/api/brightdata/serp/local` | GET | Quick local Montgomery search |
| `/api/brightdata/scrape` | POST | Scrape URL as markdown |
| `/api/brightdata/capabilities` | GET | List all integrated products |
| `/api/brightdata/status` | GET | Configuration status |

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
