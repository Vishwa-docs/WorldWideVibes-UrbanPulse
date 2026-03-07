# UrbanPulse — Pitch Script (3–5 Minutes)

## 0:00–0:30 | Hook + Problem

Hi judges, I'm presenting **UrbanPulse** — an AI-powered workforce and economic opportunity copilot for Montgomery, Alabama.

Cities collect tons of data, but residents, businesses, educators, and city teams still can't easily turn that data into clear next steps. UrbanPulse closes that gap by combining **Montgomery Open Data** with **Bright Data web signals** and **Azure OpenAI** to deliver role-specific, evidence-backed recommendations.

## 0:30–1:00 | Challenge Alignment

This directly addresses **Workforce, Business & Economic Growth**:

- **Residents** get career growth zones and training pathways.
- **Entrepreneurs** get demand, competition, and location intelligence.
- **City staff** get prioritized corridor interventions with equity weighting.
- **Education partners** get program-to-demand alignment.

We use both required data pillars:
1. City of Montgomery Open Data (ArcGIS REST — 311 requests, business licenses, foot traffic, visitor origin)
2. Bright Data **4 products**: Web Scraper (POI signals), SERP API (competitive intelligence), Web Unlocker (page scraping), and MCP Server (AI agent access)

## 1:00–2:40 | Live Product Walkthrough

I'll show four flows in one interface:

**1. Role Tabs**
- Switch between Resident, Entrepreneur, City Staff, and Education.
- Same data pipeline, different decision lens — scoring weights shift per role.

**2. Scenario + Natural Language Query**
- Choose a scenario, then ask something like: "Best grocery opportunity near underserved neighborhoods."
- The AI processes the query through the role-tuned recommendation engine.

**3. Recommendations with Scores**
- UrbanPulse ranks properties by Resident Fit, Business Opportunity, City Impact, and overall score.
- Each card shows top factors — not a black box.

**4. Evidence & Trust Panel**
- Every recommendation includes source-level evidence cards.
- You see source type (ArcGIS, Bright Data, Census), confidence percentage, and live vs cached status.
- Critical for public-sector trust and decision transparency.

**5. Signal Refresh + Change Feed**
- Hit "Refresh Signals" to pull fresh Bright Data web signals.
- Delta engine shows what changed in the last 48 hours — staff act on movement, not snapshots.

Then I switch to the **Site Selection Workspace**:
- Interactive map with 10 toggleable data layers.
- Montgomery ArcGIS overlays: 311 requests, business licenses, foot traffic, vacant reports.
- Click any property for a full scorecard.

Finally, the **City Insights** page:
- Interactive recharts dashboard — business licenses by type, foot traffic, 311 requests, score histogram, workforce breakdown.
- Radar chart directly comparing business licenses vs foot traffic (a core challenge question).
- **Web Intelligence panel** — live SERP search for Montgomery's business landscape, URL scraper, and full Bright Data capabilities view.

## 2:40–3:30 | Originality + Social Impact

What makes this different:
- Not just a map, not just a chatbot, not just a dashboard.
- It's a **multi-role AI copilot with explainability** — every score has evidence, every recommendation has provenance.

Social impact:
- Equity-weighted scoring surfaces opportunities in underserved areas first.
- Residents can identify practical pathways to career growth.
- Small businesses make data-driven launch decisions.
- City teams prioritize limited resources for maximum equity and economic return.

## 3:30–4:20 | Commercial Potential

Montgomery is our launch customer model.

UrbanPulse can replicate to any city through:
- Configurable data connectors (any ArcGIS portal + Bright Data + Census)
- Role-based scoring engine with tunable weights
- Shared copilot workflow with local dataset mappings

Business model:
- SaaS per city/department
- Optional workforce/education partner seats
- Expansion to universities, NGOs, and workforce development boards

## 4:20–4:45 | Close

UrbanPulse is a production-feel civic AI tool that is:
- Challenge-aligned — built on Montgomery data + Bright Data (4 products)
- Design-forward — professional UX with evidence transparency
- Operationally useful — real recommendations, not just visualizations
- Commercially scalable — city-agnostic architecture

Thank you.
