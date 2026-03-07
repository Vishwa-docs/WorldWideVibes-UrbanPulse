# UrbanPulse — Submission Brief

## Problem Statement

Montgomery, Alabama (pop. 200,603) has a **19.7% poverty rate** — nearly 1 in 5 residents. Median household income is $57,300, below the national $75,149. The city publishes 60+ datasets through its ArcGIS open data portal, but no tool exists to fuse this data with web intelligence and deliver actionable, role-specific guidance. Data is abundant but fragmented across disconnected systems. UrbanPulse fills that gap.

## Challenge Track

**Workforce, Business & Economic Growth** — UrbanPulse directly addresses three challenge problems:
1. **Compare business licenses with foot traffic trends** — cross-references Montgomery business license data with Most Visited Locations + Visitor Origin. Radar chart overlays licenses vs foot traffic.
2. **Identify and address vacant properties** — surfaces vacant/blighted parcels from 311 reports + code violations + property data, scores each for redevelopment potential.
3. **Analyze and improve usage of city-owned properties** — highlights surplus and city-owned parcels with opportunity scores and equity weighting.

## Target Users
- **Residents / Jobseekers** — Identify where job growth concentrates and which training programs align with local demand.
- **Entrepreneurs / Small Businesses** — Prioritize business types and locations using demand, competition, and foot-traffic context.
- **City Staff** — Prioritize corridor interventions and vacant properties with highest social + economic return.
- **Education / Workforce Partners** — Align training programs to current hiring signals and skills gaps.

## Data Sources

### Montgomery Open Data (8 ArcGIS REST endpoints — no auth, free):
| Dataset | Endpoint |
|---|---|
| 311 Service Requests | `mgmgis.montgomeryal.gov/.../Received_311_Service_Request/FeatureServer/0` |
| Business Licenses | `mgmgis.montgomeryal.gov/.../Business_License/FeatureServer/0` |
| Most Visited Locations | `services7.arcgis.com/.../Most_Visited_Locations/FeatureServer/0` |
| Visitor Origin | `services7.arcgis.com/.../Visitors_Origin/FeatureServer/0` |
| Code Violations | `mgmgis.montgomeryal.gov/.../Code_Violations/FeatureServer/0` |
| City-Owned Properties | `mgmgis.montgomeryal.gov/.../City_Owned_Properities/FeatureServer/0` |
| Construction Permits | `mgmgis.montgomeryal.gov/.../Construction_Permits/FeatureServer/0` |
| Opportunity Zones | `services7.arcgis.com/.../Opportunity_Zones/FeatureServer/0` |

All 8 endpoints return **100% live data** — zero mock or simulated fallbacks.

### Web Data (Bright Data — 4 products):
- **Web Scraper (Datasets API)** — Google Maps POI & review data collection
- **SERP API** — Local search engine results for competitive/market intelligence
- **Web Unlocker** — Scrape any public webpage as clean markdown for AI enrichment
- **MCP Server** — AI agent web data access via Model Context Protocol

### Federal + Weather Data:
- **US Census ACS API** — 31 demographic/workforce variables (income, education, commuting, transportation, housing)
- **Google Places API** — Walk score computation and nearby amenity density
- **Open-Meteo** — Real-time weather conditions + 7-day forecast (free, no key)

## AI Components
- **Role-based recommendation engine** — 4 roles (Resident, Entrepreneur, City Staff, Education) with tuned scoring weights.
- **Scenario selector** — General, Grocery, Clinic, Daycare, Coworking — shifts scoring per use-case.
- **Azure OpenAI GPT-4o-2** — AI copilot for recommendations and agent chat.
- **Deterministic fallback** — Full template-based response service when LLM keys are unavailable.
- **Signal delta engine** — Tracks 48-hour activity changes using Bright Data refresh.
- **AI Agent Chat** — Collapsible natural-language copilot in Site Selection Workspace.
- **7 recharts visualizations** — business license distribution, foot traffic, 311 requests, score distribution, workforce breakdown, property types, and radar chart (licenses vs foot traffic).

## Judging Alignment

**Total: 35 points**

| Criterion | Max | Our Approach |
|---|---|---|
| **Relevance to Challenge** | 10 | 3+ challenge problems addressed. **8 ArcGIS endpoints** (all live) + Census (31 vars) + Weather + Bright Data (4 products). |
| **Quality & Design** | 10 | Professional dark-gradient UI, 4-role architecture, 7 recharts visualizations, **14-layer interactive map**, AI Agent Chat, 137 tests passing, 0 TS errors, clean build. |
| **Originality** | 5 | No existing civic AI copilot for site selection. Equity-weighted scoring. Radar chart comparing licenses vs foot traffic. Multi-role persona with scenario weights. |
| **Social Impact** | 5 | Equity-first scoring surfaces food deserts, vacant parcels, underserved neighborhoods. Directly addresses Montgomery's 19.7% poverty rate. |
| **Commercial Potential** | 5 | SaaS tiers: Starter $2K/mo, Pro $5K/mo, Enterprise $10K–15K/mo. Undercuts Esri Hub ($25K+/yr). 85% gross margins. TAM: 19,500+ municipalities. [Full business model](business-model.md). |

## Commercialization Path

See [business-model.md](business-model.md) for detailed pricing, unit economics, and 3-year revenue projections.

**Summary**: Montgomery is the launch customer. City-agnostic architecture (`config/cities/montgomery.json`) supports any city with an ArcGIS portal. SaaS pricing from $2K–15K/mo per city. Target $4.3M ARR by Year 3 with 80 city deployments.

## Tech Stack
- **Frontend**: React 19 + TypeScript 5.9 + Vite 7.3 + Tailwind CSS v4 + Leaflet + Recharts 3.x
- **Backend**: Python 3.11 + FastAPI + SQLModel + SQLite
- **AI**: Azure OpenAI (GPT-4o-2) with deterministic fallback
- **Data**: 8 Montgomery ArcGIS REST APIs + Census ACS (31 vars) + Google Places + Open-Meteo + Bright Data (4 products)

## Live Deployment
- **Frontend**: https://urbanpulse-chi.vercel.app
- **Backend**: https://urbanpulse-api-production.up.railway.app
- **Repository**: https://github.com/Vishwa-docs/World-Wide-Vibes
