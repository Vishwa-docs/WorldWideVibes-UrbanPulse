# Free-Tier Deployment (Vercel + Railway)

## Live URLs
- **Frontend**: https://urbanpulse-chi.vercel.app
- **Backend**: https://urbanpulse-api-production.up.railway.app
- **Repository**: https://github.com/Vishwa-docs/World-Wide-Vibes

---

## Frontend (Vercel)

### Via CLI (already deployed)
```bash
npm i -g vercel
cd World-Wide-Vibes
vercel --yes --prod
```

### Via Dashboard
1. Go to [vercel.com](https://vercel.com) → Import Git Repository
2. Select `Vishwa-docs/World-Wide-Vibes`
3. Framework preset: **Vite**
4. Build command: `cd frontend && npm install && npm run build`
5. Output directory: `frontend/dist`
6. Environment variable:
   - `VITE_API_BASE_URL` = `https://urbanpulse-api-production.up.railway.app`

The `vercel.json` in the repo root configures this automatically.

---

## Backend (Railway)

### Via CLI
```bash
brew install railway
railway login
railway init --name urbanpulse-api
railway service urbanpulse-api
railway domain   # generates public URL
railway up --detach
```

### Via Dashboard
1. Go to [railway.com](https://railway.com) → New Project → Deploy from GitHub Repo
2. Select `Vishwa-docs/World-Wide-Vibes`
3. Railway auto-detects the `Dockerfile` in the repo root
4. Add environment variables:
   - `CORS_ORIGINS` = `https://urbanpulse-chi.vercel.app`
   - `PORT` = `8000`
   - Optional: `AZURE_OPENAI_*`, `BRIGHTDATA_*`, `CENSUS_API_KEY`, `GOOGLE_PLACES_API_KEY`
5. Generate a public domain under Settings → Networking

The `Dockerfile` and `railway.toml` in the repo root handle build + start automatically.

---

## Environment Variables

### Backend (Railway)
| Variable | Required | Description |
|----------|----------|-------------|
| `PORT` | Auto | Railway injects this automatically |
| `CORS_ORIGINS` | Yes | Set to your Vercel frontend URL |
| `AZURE_OPENAI_ENDPOINT` | Optional | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | Optional | Azure OpenAI key |
| `AZURE_OPENAI_DEPLOYMENT` | Optional | e.g. `gpt-4o-2` |
| `AZURE_OPENAI_API_VERSION` | Optional | e.g. `2024-12-01-preview` |
| `BRIGHTDATA_API_TOKEN` | Optional | Bright Data API token |
| `BRIGHTDATA_SERP_ZONE` | Optional | SERP zone name |
| `BRIGHTDATA_UNLOCKER_ZONE` | Optional | Web Unlocker zone name |
| `GOOGLE_PLACES_API_KEY` | Optional | Google Places key |
| `CENSUS_API_KEY` | Optional | US Census ACS key |

### Frontend (Vercel)
| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes | Full Railway backend URL (e.g. `https://urbanpulse-api-production.up.railway.app`) |

---

## Reliability Notes
- App runs even if LLM/Bright Data keys are missing:
  - LLM: deterministic fallback mode (template-based responses).
  - Bright Data: placeholder web signal data.
  - ArcGIS: fully live (free, no auth required) — 8 endpoints, 100% real data.
  - Census & Weather: fully live (free).
- Database: SQLite file (created automatically on first start).
- Health check: `GET /api/health` returns `{"status": "ok"}`.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Railway build fails | Check `Dockerfile` is in repo root. Railway must detect it as Docker builder. |
| Frontend shows CORS errors | Set `CORS_ORIGINS` on Railway to your exact Vercel URL (with `https://`). |
| API returns empty data | ArcGIS endpoints are free and public — check network connectivity. |
| LLM responses are templated | Add `AZURE_OPENAI_*` env vars to Railway for GPT-4o-2 responses. |
| Frontend can't reach backend | Set `VITE_API_BASE_URL` in Vercel env vars. Redeploy after changing. |
