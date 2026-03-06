# UrbanPulse 🏙️

**Agentic Site-Selection Intelligence for Montgomery, Alabama**

> Built for the World Wide Vibes GenAI.Works Hackathon — March 2026

UrbanPulse is an AI-powered site-selection web application that helps city planners and entrepreneurs find the best locations for businesses and community services in Montgomery, AL. It combines open data, web intelligence (via Bright Data), and multi-agent AI analysis to deliver actionable location insights.

## 🎯 Challenge Alignment

This project addresses the GenAI.Works hackathon challenge by:
- **Using City of Montgomery Open Data Portal** as primary data source
- **Integrating Bright Data** for web-scraped activity signals (POIs, reviews, competition)
- **Deploying multi-agent AI** for intelligent, context-aware recommendations
- **Targeting real social impact** through equity-focused location analysis

## ✨ Features (14+)

### Core Product
1. **Dual Persona Workspaces** — City Console (planners) vs Entrepreneur Studio (businesses)
2. **Vacancy & Utilization Map** — Interactive Leaflet map with smart layers
3. **Property Scorecards** — Multi-dimensional scoring (0-10) with AI narratives
4. **Scenario Templates** — Grocery, Clinic, Daycare, Coworking presets

### Agentic AI
5. **UrbanPulse Orchestrator** — Natural-language copilot powered by Gemini
6. **Specialist Lens Agents** — Equity, Risk/Safety, and BizCoach sub-agents
7. **Comparable Sites Explorer** — Side-by-side AI-powered comparison
8. **Guided Story Mode** — AI-generated narrative city tours

### Data & Insights
9. **Bright Data Activity Layer** — POI counts, reviews, competition density
10. **Equity & Service Gap Overlay** — Underserved area visualization
11. **City Project Awareness** — Infrastructure investment proximity badges
12. **Watchlists & Alerts** — Star properties with refresh capability

### Collaboration & Export
13. **Exportable Reports** — CSV export with scores and rankings
14. **"Bring Your City" Connector** — Pluggable city configuration system

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS |
| Mapping | Leaflet (react-leaflet) |
| Backend | Python 3.11+ / FastAPI |
| Database | SQLite (via SQLModel/SQLAlchemy) |
| AI/LLM | Google Gemini (swappable) |
| Web Data | Bright Data Crawl/Scraper API |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python -m scripts.seed_sample  # Seed demo data
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app will be available at http://localhost:5173

### Environment Variables

#### Backend (.env)
| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Optional (fallback mode available) |
| `BRIGHTDATA_API_TOKEN` | Bright Data API token | Optional (simulated mode available) |
| `DATABASE_URL` | SQLite connection string | No (defaults to local file) |

#### Frontend (.env)
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

## 📊 Data Sources

- **Montgomery Open Data Portal**: https://opendata.montgomeryal.gov
- **Bright Data**: Web-scraped POI, review, and competition data
- **Sample Data**: 50 seeded properties with realistic Montgomery addresses

## 🏆 Hackathon Judging Alignment

| Criterion | How UrbanPulse Addresses It |
|-----------|---------------------------|
| **Consistency** | Built on Montgomery's open data, directly addresses the challenge |
| **Quality & Design** | Professional UI, clean code, comprehensive API |
| **Originality** | Multi-agent AI copilot with specialist "lens" agents |
| **Social Impact** | Equity-first scoring, service gap analysis, underserved areas |
| **Commercialization** | "Bring Your City" connector, extensible architecture |
| **Bright Data (+3)** | Integrated web scraping for real-world activity signals |

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings management
│   │   ├── database.py          # SQLite setup
│   │   ├── models/              # SQLModel schemas
│   │   ├── routes/              # API endpoints
│   │   └── services/            # Business logic
│   │       ├── scoring.py       # Scoring engine
│   │       ├── brightdata_client.py  # Bright Data integration
│   │       ├── llm_service.py   # LLM abstraction
│   │       └── agents/          # AI agents
│   ├── scripts/                 # Data ingestion
│   ├── tests/                   # Backend tests
│   └── data/raw/               # Raw data files
├── frontend/
│   └── src/
│       ├── components/          # React components
│       ├── pages/               # Page views
│       ├── hooks/               # Custom hooks
│       ├── services/            # API client
│       └── types/               # TypeScript types
├── config/cities/               # City configurations
└── docs/                        # Documentation
```

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest tests/ -v

# Frontend build check
cd frontend && npm run build
```

## 📄 License

MIT — Built with ❤️ for the World Wide Vibes Hackathon
