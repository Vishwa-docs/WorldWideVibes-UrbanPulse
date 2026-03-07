# UrbanPulse — Pitch Script (3–5 Minutes)

## 0:00–0:30 | Hook + Problem

Hi judges, I'm presenting **UrbanPulse** — an AI-powered workforce and economic opportunity copilot for Montgomery, Alabama.

Montgomery has a 19.7% poverty rate — nearly one in five residents. The city publishes 60+ datasets through its ArcGIS open data portal, but no tool exists to fuse that data with web intelligence and deliver clear, role-specific next steps. UrbanPulse closes that gap by combining **8 Montgomery ArcGIS endpoints**, **Bright Data web signals (4 products)**, **US Census ACS (31 variables)**, and **Azure OpenAI (GPT-4o-2)** into one civic-intelligence platform.

## 0:30–1:00 | Challenge Alignment

This directly addresses **Workforce, Business & Economic Growth** — three challenge problems in one product:

1. **Compare business licenses with foot traffic trends** — cross-references license data with Most Visited Locations + Visitor Origin. Radar chart overlays licenses vs foot traffic.
2. **Identify and address vacant properties** — surfaces vacant/blighted parcels from 311 reports + code violations, scores each for redevelopment potential.
3. **Analyze and improve usage of city-owned properties** — highlights surplus parcels with opportunity scores and equity weighting.

We use both required data pillars:
- City of Montgomery Open Data — **8 ArcGIS REST endpoints**, all returning live data, no mock fallbacks
- Bright Data **4 products**: Web Scraper, SERP API, Web Unlocker, MCP Server

## 1:00–2:40 | Live Product Walkthrough

**1. Four Role Lenses**
- Switch between Resident, Entrepreneur, City Staff, and Education tabs.
- Same data pipeline, different decision lens — scoring weights shift per role.

**2. Scenario Selector**
- Choose General, Grocery, Clinic, Daycare, or Coworking.
- Scoring weights adapt to the use-case — a grocery scenario boosts food-desert proximity.

**3. Auto-Loaded Recommendations**
- UrbanPulse ranks properties automatically by Resident Fit, Business Opportunity, City Impact, and overall score.
- Each card shows top contributing factors — not a black box.

**4. Data Sources & Trust Panel**
- Every recommendation shows source-level traceability: source type, freshness timestamp, confidence score, live vs cached status.
- Critical for public-sector transparency.

**5. Signal Change Feed**
- Delta engine tracks what changed in the last 48 hours — staff act on movement, not snapshots.

Then I switch to the **Site Selection Workspace**:
- Interactive Leaflet map with **14 toggleable data layers** — all 8 ArcGIS overlays plus Census, weather, scoring layers.
- **AI Agent Chat** — collapsible copilot for natural-language questions about properties and opportunities.
- Click any property for a full scorecard. Save to watchlist for side-by-side comparison.

Finally, the **City Insights** page:
- **7 recharts visualizations** — business licenses by type, foot traffic hotspots, 311 requests by category, property score distribution, workforce industry breakdown, property types.
- **Radar chart** directly comparing business licenses vs foot traffic (addresses the challenge question).
- **Web Intelligence panel** — SERP search, URL scraper, and Bright Data capabilities view.
- **Weather widget** — real-time conditions + 7-day forecast.
- **Enhanced demographics** — 31 Census ACS variables: education, commuting, transportation.

## 2:40–3:30 | Originality + Social Impact

What makes this different:
- Not just a map, not just a chatbot, not just a dashboard.
- It's a **multi-role AI copilot with explainability** — every score has evidence, every recommendation has provenance.
- No existing product combines live city open data + web-scraped signals + AI recommendations + equity scoring.

Social impact:
- **Equity-first scoring** surfaces opportunities in underserved areas first — food deserts, vacant parcels, high-poverty neighborhoods.
- Directly addresses Montgomery's **19.7% poverty rate** and economic disinvestment.
- Four stakeholder lenses ensure broad community benefit — residents, entrepreneurs, city staff, educators all get value.

## 3:30–4:20 | Commercial Potential

Montgomery is our launch customer model. The architecture is **city-agnostic by design**:
- `config/cities/montgomery.json` holds all endpoint URLs, Census FIPS codes, and map bounds.
- Adding a new city = one config file, zero code changes. Onboarding time: < 1 week.

**Pricing** (undercuts incumbents):
- Starter: **$2K/mo** ($24K/yr) — vs Esri Hub at $25K–$100K/yr
- Professional: **$5K/mo** ($60K/yr) — includes AI Agent Chat + Bright Data signals
- Enterprise: **$10K–15K/mo** — multi-city, SSO, SLA

**Unit economics**: ~$450/mo COGS per city → **85% gross margins** (most data sources are free).

**Revenue projection**: 5 cities Y1 ($180K) → 25 cities Y2 ($1.2M) → 80 cities Y3 ($4.3M ARR).

**TAM**: 19,500+ US municipalities, $105B annual municipal IT spend.

## 4:20–4:45 | Close

UrbanPulse is a production-quality civic AI tool that is:
- **Challenge-aligned** — 3+ challenge problems, 8 ArcGIS endpoints, 4 Bright Data products
- **Statistics-backed** — 19.7% poverty rate, $57K median income, 200K+ population
- **Design-forward** — professional dark-gradient UI, 137 tests, 0 TS errors, clean build
- **Commercially viable** — $4.3M ARR by Year 3, 85% margins, city-agnostic architecture

Thank you.
