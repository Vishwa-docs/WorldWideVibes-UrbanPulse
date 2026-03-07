# UrbanPulse Setup Guide

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | 2.x | `git --version` |

---

## 1. Clone the Repository

```bash
git clone <repo-url> World-Wide-Vibes
cd World-Wide-Vibes
```

---

## 2. Backend Setup

### Create a Virtual Environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
# .venv\Scripts\activate     # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **FastAPI** + **Uvicorn** — Web framework and ASGI server
- **SQLModel** + **SQLAlchemy** — ORM and database layer
- **Pydantic** + **pydantic-settings** — Validation and config
- **httpx** — Async HTTP client (for Bright Data, ArcGIS, Census)
- **openai** — Azure OpenAI SDK
- **pytest** — Testing framework

### Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required for AI features (optional — fallback mode works without it)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-2
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Required for live web intelligence (optional — simulated mode works without it)
BRIGHTDATA_API_TOKEN=your_brightdata_api_token_here
BRIGHTDATA_SERP_ZONE=your_serp_zone_name
BRIGHTDATA_UNLOCKER_ZONE=your_unlocker_zone_name

# Census & Places (optional)
CENSUS_API_KEY=your_census_key_here
GOOGLE_PLACES_API_KEY=your_places_key_here

# Database (optional — defaults to local SQLite file)
DATABASE_URL=sqlite:///./urbanpulse.db

# CORS origins (optional — defaults include localhost:5173)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

> **Tip**: The app runs in fallback mode without any API keys.
> Azure OpenAI falls back to template-based responses. Bright Data uses placeholder signals.
> ArcGIS, Census, and Weather data remain fully live (free, no keys required).

### Seed the Database

```bash
python -m scripts.seed_sample
```

This creates `urbanpulse.db` with 50 properties, 100 incidents, 20 service
locations, 5 city projects, pre-computed scores, and sample watchlist items.

### Start the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

Verify it's running:
```bash
curl http://localhost:8000/api/health
# → {"status": "healthy", "version": "1.0.0"}
```

The interactive API docs are available at http://localhost:8000/docs

---

## 3. Frontend Setup

Open a new terminal:

```bash
cd frontend
npm install
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Start the Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

---

## 4. API Key Configuration

### Azure OpenAI API Key

1. Go to https://portal.azure.com → **Azure OpenAI** service
2. Create an OpenAI resource (or use an existing one)
3. Deploy a model (e.g., **GPT-4o**)
4. Copy the **endpoint**, **key**, and **deployment name** into `backend/.env`

The app uses **Azure OpenAI GPT-4o** for:
- AI copilot responses (Orchestrator)
- Equity analysis narratives
- Risk assessment narratives
- Business coaching advice
- Story mode city tours

**Without keys**: The `FallbackLLMService` generates deterministic template-based responses
that demonstrate all features without making API calls.

### Bright Data API Token

1. Sign up at https://brightdata.com
2. Navigate to **API** → **API Tokens** in the dashboard
3. Create a new token with Web Scraper API permissions
4. Copy the token into `backend/.env` as `BRIGHTDATA_API_TOKEN`
5. Set up SERP and Web Unlocker zones in the dashboard, add zone names to `.env`

UrbanPulse uses **4 Bright Data products**:

| Product | Purpose |
|---------|--------|
| Web Scraper (Datasets API) | Google Maps POI & review data for activity signals |
| SERP API | Local search engine results for competitive intelligence |
| Web Unlocker | Scrape any public page as clean markdown for AI enrichment |
| MCP Server | AI agent web data access via Model Context Protocol |

**Without a token**: The `BrightDataClient` generates deterministic placeholder data
based on coordinates, so the scoring pipeline works in a basic demo configuration.
**Note:** All ArcGIS, Census, and Weather data remains fully live regardless.

---

## 5. Database Management

### Using Real City Data

If you have real Montgomery data from the Open Data Portal:

```bash
# Place CSV files in the data directory
cp parcels.csv backend/data/raw/
cp incidents.csv backend/data/raw/
cp city_projects.csv backend/data/raw/

# Run the ingestion script
cd backend
python -m scripts.ingest_montgomery
```

The ingestion script reads column mappings from `config/cities/montgomery.json`
and normalizes the data into the UrbanPulse schema.

### Reseeding the Database

To reset to demo data:

```bash
cd backend
rm urbanpulse.db              # Delete existing database
python -m scripts.seed_sample  # Regenerate with fresh sample data
```

### Recomputing Scores

After ingesting new data or changing scenario weights:

```bash
curl -X POST http://localhost:8000/api/scores/compute \
  -H "Content-Type: application/json" \
  -d '{"scenario": "general", "persona": "city_console"}'
```

Or compute scores for specific scenarios:
```bash
for scenario in general grocery clinic daycare coworking; do
  curl -X POST http://localhost:8000/api/scores/compute \
    -H "Content-Type: application/json" \
    -d "{\"scenario\": \"$scenario\", \"persona\": \"city_console\"}"
done
```

---

## 6. Running Tests

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

Current test modules:
- `test_health.py` — Health endpoint
- `test_api.py` — Property and scoring API endpoints
- `test_scoring.py` — Scoring engine logic
- `test_agents.py` — AI agent orchestration
- `test_brightdata.py` — Bright Data client (4 products)
- `test_copilot_api.py` — Copilot API endpoints
- `test_montgomery.py` — Montgomery ArcGIS data
- `test_new_features.py` — Additional feature tests

### Frontend Build Check

```bash
cd frontend
npm run build
```

---

## 7. Running Both Services Together

For development, run the backend and frontend in separate terminals:

**Terminal 1 — Backend**:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend**:
```bash
cd frontend
npm run dev
```

---

## Common Troubleshooting

### "ModuleNotFoundError: No module named 'app'"

Make sure you're running from the `backend/` directory:
```bash
cd backend
python -m scripts.seed_sample  # Note: use -m flag
```

### "CORS error" in browser console

Ensure the frontend URL is included in `CORS_ORIGINS` in `backend/.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### "sqlite3.OperationalError: no such table"

The database hasn't been initialized. Either:
```bash
python -m scripts.seed_sample   # Creates tables + sample data
```
Or start the backend server (tables are created on startup via lifespan hook):
```bash
uvicorn app.main:app --reload
```

### Port already in use

```bash
# Find what's using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### API keys not loading

- Ensure `.env` is in the `backend/` directory (not the project root)
- Check for trailing whitespace in key values
- Restart the backend server after changing `.env`

### Frontend can't connect to backend

- Verify backend is running: `curl http://localhost:8000/api/health`
- Check `VITE_API_BASE_URL` in `frontend/.env` matches the backend port
- Restart the frontend dev server after changing `.env`

### Bright Data returning placeholder data

Check the status endpoint:
```bash
curl http://localhost:8000/api/brightdata/status
```
If `"mode": "simulated"`, set a valid `BRIGHTDATA_API_TOKEN` in `backend/.env`.
**Note:** ArcGIS endpoints always use live data regardless of Bright Data configuration.
