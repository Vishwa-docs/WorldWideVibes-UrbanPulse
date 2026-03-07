# UrbanPulse — Frontend

React + TypeScript SPA for the UrbanPulse civic-intelligence platform.

## Tech

| Tool | Version |
|------|---------|
| React | 19 |
| TypeScript | 5.9 |
| Vite | 7.3 |
| Tailwind CSS | v4 |
| Recharts | 3.x |
| Leaflet | 1.9 |

## Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `CopilotPage` | Opportunity Copilot — role-based recommendations |
| `/site` | `DashboardPage` | Site Selection — Leaflet map with 14 layers + AI Agent Chat |
| `/compare` | `ComparePage` | Side-by-side property comparison |
| `/story` | `StoryPage` | Story mode narrative |
| `/insights` | `InsightsPage` | Analytics charts + Web Intelligence |

## Key Components

- **`Insights/AnalyticsCharts.tsx`** — 7 recharts visualizations (bar, pie, radar, histogram)
- **`Insights/WebIntelligence.tsx`** — SERP search + URL scraper + Bright Data capabilities
- **`Insights/DemographicsPanel.tsx`** — Census ACS demographics display (31 variables)
- **`Agent/AgentChat.tsx`** — AI copilot chat (collapsible, in Site Workspace)
- **`Map/LayerControls.tsx`** — 14 toggleable data layers (collapsible)
- **`Map/`** — Leaflet map, property markers

## API Client

All backend calls go through `src/services/api.ts` — typed functions with Axios, auto-configured base URL.

## Development

```bash
npm install
npm run dev          # dev server on :5173
npm run build        # production build
npx tsc --noEmit     # type-check only
```

## Build

```bash
npm run build        # outputs to dist/
```

Static files in `dist/` are served by FastAPI in production (unified Railway deployment).

## Environment

The frontend reads `VITE_API_BASE_URL` at build time. Defaults to `http://localhost:8000` in development.
