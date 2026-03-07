# UrbanPulse — Demo & Recording Guide

*Combines demo script + video recording instructions in one place.*

---

## Setup Checklist

- [ ] Backend running: `cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8000`
- [ ] Frontend running: `cd frontend && npm run dev` (opens on port 5173)
- [ ] Browser open to `http://localhost:5173`
- [ ] Screen recorder ready (QuickTime / OBS / Loom)
- [ ] Browser zoom: 90–100%, resolution: 1920×1080+
- [ ] Close unnecessary tabs and notifications

### Pre-warm Data
1. Open Copilot (`/`) → let recommendations auto-load
2. Navigate to `/site` and let the map load fully
3. Navigate to `/insights` and let charts render
4. Return to `/` — everything loads instantly now

---

## 3-Minute Demo Script

### 0:00–0:30 — Hook & Challenge Alignment

**Show**: Landing page with role tabs and recommendations.

**Say**: "UrbanPulse is an AI-powered workforce and economic opportunity copilot for Montgomery, Alabama. Montgomery has a 19.7% poverty rate — nearly 1 in 5 residents. The city publishes 60+ datasets, but no tool fuses this data with web intelligence to deliver role-specific recommendations. UrbanPulse solves that."

**Action**: Point to the role tabs and "Connected" status indicator.

**Say**: "This directly targets three challenge problems: compare business licenses with foot traffic, identify vacant properties, and analyze city-owned property usage."

### 0:30–0:50 — Role-Based Intelligence

**Action**: Click through each role tab — Resident, Entrepreneur, City Staff, Education.

**Say**: "Four stakeholder lenses share the same data pipeline but apply different scoring weights. A resident sees career growth zones. An entrepreneur sees demand gaps. City staff see corridor priorities. Educators see skills alignment."

**Note**: Pause on each tab to show recommendations changing.

### 0:50–1:20 — Scenario Selector + Auto-Loaded Recommendations

**Action**: Select "Grocery" from the scenario dropdown. Watch recommendations reload.

**Say**: "The scenario selector changes scoring weights. Selecting 'Grocery' boosts food-desert proximity and foot traffic. Properties are ranked by Resident Fit, Business Opportunity, and City Impact — and the platform explains why each scored high."

**Action**: Point to the scored recommendation cards and top factor pills.

### 1:20–1:50 — Data Sources & Trust

**Action**: Point to the "Data Sources & Trust" sidebar panel. Scroll through sources.

**Say**: "Every recommendation carries source-level traceability — the data source, whether it's live or cached, freshness timestamps, and confidence scores. This is critical for public-sector trust. No black boxes."

### 1:50–2:10 — Site Selection Map + AI Agent Chat

**Action**: Navigate to `/site` (click "Site Map" in navigation).

**Say**: "The Site Selection Workspace is an interactive map with 14 toggleable data layers — all 8 Montgomery ArcGIS overlays plus Census, weather, and scoring layers."

**Action**: Toggle a few layers on/off. Click a property marker for the scorecard. Open the AI Agent Chat panel.

**Say**: "The collapsible AI Agent Chat lets you ask natural-language questions about properties and opportunities."

### 2:10–2:30 — City Insights & Analytics Charts

**Action**: Navigate to `/insights`.

**Say**: "City Insights provides 7 interactive visualizations. Business licenses by type, foot traffic hotspots, 311 service requests, property scores, workforce breakdown, and property types."

**Action**: Scroll to the radar chart.

**Say**: "This radar chart directly addresses the challenge: comparing business licenses with foot traffic trends — where businesses are licensed versus where people actually go."

### 2:30–2:50 — Web Intelligence (Bright Data 4 Products)

**Action**: Scroll to the Web Intelligence panel on `/insights`.

**Say**: "All four Bright Data products are integrated. SERP API searches Montgomery's business landscape. Web Unlocker scrapes any public URL as clean markdown. Web Scraper collects POI signals. MCP Server enables AI agent web access."

**Action**: Click a preset SERP query → show results.

### 2:50–3:00 — Impact & Commercial Story

**Action**: Navigate to `/business` (click "Business Model" in navigation).

**Say**: "The commercial pitch is built right into the app. UrbanPulse shows market sizing, pricing tiers, competitive landscape, unit economics, and 3-year revenue projections — all in a polished in-app page."

**Action**: Scroll through the pricing tiers and revenue projections.

**Say**: "SaaS pricing from $2K to $15K per month — undercutting Esri Hub while adding AI and web intelligence. 85% gross margins because most data sources are free. Projected $4.3M ARR by Year 3 with 80 city deployments. The architecture is city-agnostic — adding a new city is one config file, zero code changes, less than one week to onboard."

**Say**: "Thank you."

---

## Tips for a Winning Video

1. **Pacing** — Don't rush. Let UI transitions finish before talking.
2. **Mouse** — Move the cursor deliberately to draw attention.
3. **Audio** — Quiet room. Lapel mic or headset.
4. **Errors** — If something doesn't load, say "graceful degradation" — it's a feature.
5. **Energy** — Confident, not rushed.
6. **Resolution** — 1080p minimum, 4K ideal.

## Post-Recording

1. Trim dead air at start/end
2. Add 3-second title card: **UrbanPulse — Workforce & Economic Opportunity Copilot**
3. Export as MP4, H.264, 1080p
4. Upload to YouTube (unlisted) or Loom
5. Include the link in the submission form
