# UrbanPulse — Submission Brief

## Problem Statement

Montgomery, Alabama (pop. 200,603) has a 19.7% poverty rate and pockets of economic disinvestment — vacant storefronts, food deserts, and underserved neighborhoods. The city publishes rich open data (ArcGIS portal, business licenses, foot traffic, 311 requests), but no tool exists to fuse this data with real-time web intelligence and deliver actionable, role-specific guidance. UrbanPulse fills that gap.

## Challenge Track

**Workforce, Business & Economic Growth** — UrbanPulse directly addresses three challenge problems:
1. **Compare business licenses with foot traffic trends** — cross-references Montgomery business license data with foot traffic and visitor origin data to identify demand-supply gaps.
2. **Identify and address vacant properties** — surfaces vacant/blighted parcels from 311 reports and property data, scoring each for redevelopment potential.
3. **Analyze and improve usage of city-owned properties** — highlights surplus and city-owned parcels with opportunity scores.

## Target Users
- **Residents / Jobseekers** — Identify where job growth concentrates and which training programs align with local demand.
- **Entrepreneurs / Small Businesses** — Prioritize business types and locations using demand, competition, and foot-traffic context.
- **City Staff** — Prioritize corridor interventions and vacant properties with highest social + economic return.
- **Education / Workforce Partners** — Align training programs to current hiring signals and skills gaps.

## Data Sources

### Montgomery Open Data (ArcGIS portal — no auth, free REST APIs):
| Dataset | Endpoint |
|---|---|
| 311 Service Requests | `mgmgis.montgomeryal.gov/.../Received_311_Service_Request/FeatureServer/0` |
| Business Licenses | `mgmgis.montgomeryal.gov/.../Business_Licenses/FeatureServer/0` |
| Most Visited Locations | `services7.arcgis.com/.../Most_Visited_Locations/FeatureServer/0` |
| Visitor Origin (foot traffic) | `services7.arcgis.com/.../Visitors_Origin/FeatureServer/0` |

### Web Data (Bright Data — 4 products):
- **Web Scraper (Datasets API)** — Google Maps POI & review data collection
- **SERP API** — Local search engine results for competitive/market intelligence
- **Web Unlocker** — Scrape any public webpage as clean markdown for AI enrichment
- **MCP Server** — AI agent web data access via Model Context Protocol (documented)
- **Competition & review aggregation** — sentiment and density analysis per neighborhood

### Federal Data:
- **US Census ACS API** — Demographics, income, employment, housing vacancy by census tract (FIPS 01101)
- **Google Places API** — Walk score computation and nearby amenity density

## AI Components
- **Role-based recommendation engine** — Tuned scoring weights per user type (resident, entrepreneur, city, education).
- **Azure OpenAI GPT-4o** — Natural-language copilot for querying, narratives, and market gap analysis.
- **Evidence contract** — Every recommendation carries source metadata, freshness timestamp, confidence score, and traceability.
- **Signal delta engine** — Tracks 48-hour activity changes using Bright Data refresh.
- **Interactive analytics dashboard** — recharts-powered visualizations: business license distribution, foot traffic, 311 requests by category, property score distribution, workforce industry breakdown, and a radar chart overlaying licenses vs foot traffic (directly addressing the challenge "compare business licenses with foot traffic trends").

## Judging Alignment

| Criteria | Max | Our Approach |
|---|---|---|
| **Consistency with challenge statements** | 10 | Addresses 3+ challenge problems: business licenses vs foot traffic, vacant properties, city-owned property usage, 311 service requests. Uses 4 Montgomery ArcGIS endpoints + Census ACS + Bright Data. |
| **Quality & design** | 10 | Professional dark-gradient UI, 4-role architecture, interactive charts (recharts), 10-layer map, 128 tests passing, clean TypeScript build. |
| **Originality** | 5 | No existing civic site-selection AI copilot. Equity-weighted scoring surfaces underserved areas first. Radar chart comparing licenses vs foot traffic. |
| **Social value / impact** | 5 | Equity-first scoring. Surfaces food deserts, vacant parcels, and underserved neighborhoods. Four stakeholder lenses ensure broad community benefit. |
| **Commercialization** | 5 | SaaS per city/department. Montgomery = launch customer. City-agnostic architecture for replication. |
| **Bright Data bonus** | +3 | **4 products integrated**: Web Scraper (POI/reviews), SERP API (local search), Web Unlocker (page scraping), MCP Server (AI agent access). Interactive Web Intelligence panel in UI. Bright Data badge prominent in header. |

## Commercialization Path

**Montgomery is the launch customer. Any city with an open data portal is the addressable market.**

1. **Pilot** — Free deployment for Montgomery economic development office + ASU workforce programs.
2. **Product** — SaaS platform ($2K–5K/mo per city department). Configurable data connectors per city portal.
3. **Expansion targets** — Municipal economic development agencies, university workforce programs, small business lenders, NGOs.
4. **Go-to-market** — Partner with organizations like the National League of Cities; white-label for workforce boards.

## Tech Stack
- **Frontend**: React 19 + TypeScript 5.9 + Vite + Tailwind CSS v4 + Leaflet
- **Backend**: Python 3.11 + FastAPI + SQLModel + SQLite
- **AI**: Azure OpenAI (GPT-4o-2)
- **Data**: Montgomery ArcGIS REST APIs + Census ACS + Google Places + Bright Data Web Scraper
