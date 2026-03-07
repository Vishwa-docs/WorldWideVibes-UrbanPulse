# Deployment Guide (Railway — Unified)

## Live URL
- **App**: https://urbanpulse-api-production.up.railway.app
- **Repository**: https://github.com/Vishwa-docs/World-Wide-Vibes

The app is deployed as a **single service** on Railway. The multi-stage Dockerfile builds the React frontend and serves it from FastAPI alongside the API — no separate frontend hosting required.

---

## How It Works

The `Dockerfile` in the repo root performs a two-stage build:

1. **Stage 1 (Node)** — Installs frontend dependencies and runs `npm run build` → produces `dist/`
2. **Stage 2 (Python)** — Installs backend dependencies, copies backend code, copies the frontend `dist/` into `static/`. FastAPI serves the static files and provides the API.

All routes starting with `/api/` hit the FastAPI backend. All other routes serve the React SPA.

---

## Deploy via CLI

```bash
brew install railway
railway login
railway init --name urbanpulse-api
railway service urbanpulse-api
railway domain   # generates public URL
railway up --detach
```

## Deploy via Dashboard

1. Go to [railway.com](https://railway.com) → New Project → Deploy from GitHub Repo
2. Select `Vishwa-docs/World-Wide-Vibes`
3. Railway auto-detects the `Dockerfile` in the repo root
4. Add environment variables (see below)
5. Generate a public domain under Settings → Networking

The `Dockerfile` and `railway.toml` in the repo root handle build + start automatically.

---

## Environment Variables (Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| `PORT` | Auto | Railway injects this automatically |
| `AZURE_OPENAI_ENDPOINT` | Optional | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | Optional | Azure OpenAI key |
| `AZURE_OPENAI_DEPLOYMENT` | Optional | e.g. `gpt-4o-2` |
| `AZURE_OPENAI_API_VERSION` | Optional | e.g. `2024-12-01-preview` |
| `BRIGHTDATA_API_TOKEN` | Optional | Bright Data API token |
| `BRIGHTDATA_SERP_ZONE` | Optional | SERP zone name |
| `BRIGHTDATA_UNLOCKER_ZONE` | Optional | Web Unlocker zone name |
| `GOOGLE_PLACES_API_KEY` | Optional | Google Places key |
| `CENSUS_API_KEY` | Optional | US Census ACS key |

---

## Reliability Notes
- App runs even if LLM/Bright Data keys are missing:
  - LLM: deterministic fallback mode (template-based responses).
  - Bright Data: placeholder web signal data.
  - ArcGIS: fully live (free, no auth required) — 8 endpoints, 100% real data.
  - Census & Weather: fully live (free).
- Database: SQLite file (created automatically on first start).
- Health check: `GET /api/health` returns `{"status":"healthy"}`.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Railway build fails | Check `Dockerfile` is in repo root. Railway must detect it as Docker builder. |
| API returns empty data | ArcGIS endpoints are free and public — check network connectivity. |
| LLM responses are templated | Add `AZURE_OPENAI_*` env vars to Railway for GPT-4o-2 responses. |
| Frontend shows blank page | Check Railway build logs — Node stage must succeed. Verify `frontend/package.json` exists. |
