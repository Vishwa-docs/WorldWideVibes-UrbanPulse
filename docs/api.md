# UrbanPulse API Documentation

**Base URL**: `http://localhost:8000`

All endpoints return JSON unless otherwise noted. The API uses FastAPI and includes
auto-generated interactive docs at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Health

### `GET /api/health`

Basic service health check.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8000/api/health
```

---

## Properties

### `GET /api/properties`

List properties with optional filters and pagination.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_vacant` | bool | — | Filter by vacancy status |
| `is_city_owned` | bool | — | Filter by city ownership |
| `neighborhood` | string | — | Filter by neighborhood name |
| `property_type` | string | — | Filter by type (residential, commercial, mixed, vacant_land) |
| `scenario` | string | `"general"` | Scoring scenario for attached scores |
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `50` | Page size (1–200) |

**Response**: `PropertyResponse[]`

```json
[
  {
    "id": 1,
    "parcel_id": "MG-12345-100",
    "address": "100 Dexter Ave",
    "latitude": 32.377,
    "longitude": -86.3085,
    "property_type": "commercial",
    "zoning": "C-2",
    "is_vacant": false,
    "is_city_owned": false,
    "lot_size_sqft": 15000.0,
    "building_sqft": 8000.0,
    "assessed_value": 250000.0,
    "year_built": 1965,
    "neighborhood": "Downtown",
    "council_district": "3",
    "score": {
      "foot_traffic_score": 7.5,
      "competition_score": 6.0,
      "safety_score": 8.2,
      "equity_score": 5.5,
      "activity_index": 6.8,
      "overall_score": 6.8,
      "scenario": "general",
      "computed_at": "2026-03-06T12:00:00"
    }
  }
]
```

**Example**:
```bash
# List vacant properties in Downtown
curl "http://localhost:8000/api/properties?is_vacant=true&neighborhood=Downtown&limit=10"

# List commercial properties with grocery scenario scores
curl "http://localhost:8000/api/properties?property_type=commercial&scenario=grocery"
```

---

### `GET /api/properties/{property_id}`

Get a single property with its latest score.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | int | Property ID |

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenario` | string | `"general"` | Scoring scenario |

**Response**: `PropertyResponse`

**Example**:
```bash
curl http://localhost:8000/api/properties/1?scenario=clinic
```

---

### `GET /api/properties/{property_id}/scorecard`

Return a detailed scorecard including nearby incidents, services, and AI narrative.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | int | Property ID |

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenario` | string | `"general"` | Scoring scenario |
| `persona` | string | `"city_console"` | User persona (city_console or entrepreneur) |

**Response**: `ScorecardResponse`

```json
{
  "property": { "...PropertyResponse..." },
  "scores": {
    "foot_traffic_score": 7.5,
    "competition_score": 6.0,
    "safety_score": 8.2,
    "equity_score": 5.5,
    "activity_index": 6.8,
    "overall_score": 6.8,
    "scenario": "general",
    "computed_at": "2026-03-06T12:00:00"
  },
  "nearby_incidents": [
    {
      "id": 42,
      "incident_type": "theft",
      "latitude": 32.378,
      "longitude": -86.309,
      "severity": "low",
      "distance_km": 0.15
    }
  ],
  "nearby_services": [
    {
      "id": 5,
      "name": "Downtown Grocery",
      "service_type": "grocery",
      "latitude": 32.376,
      "longitude": -86.307,
      "distance_km": 0.25
    }
  ],
  "ai_narrative": "This property shows strong potential for..."
}
```

**Example**:
```bash
curl "http://localhost:8000/api/properties/1/scorecard?scenario=grocery&persona=entrepreneur"
```

---

## Scores

### `POST /api/scores/compute`

Recompute scores for all properties under a given scenario and persona.

**Request Body**:
```json
{
  "scenario": "grocery",
  "persona": "city_console"
}
```

**Response**: `ScoreComputeResponse`

```json
{
  "computed_count": 50,
  "scenario": "grocery",
  "persona": "city_console"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/scores/compute \
  -H "Content-Type: application/json" \
  -d '{"scenario": "grocery", "persona": "city_console"}'
```

---

### `GET /api/scores/ranked`

Return properties ranked by overall score (descending).

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenario` | string | `"general"` | Scoring scenario |
| `persona` | string | `"city_console"` | User persona |
| `limit` | int | `20` | Max results (1–200) |
| `min_score` | float | `0.0` | Minimum overall score filter |

**Response**: `RankedListResponse`

```json
{
  "items": [
    {
      "rank": 1,
      "property": { "...PropertyResponse..." },
      "overall_score": 8.75
    }
  ],
  "scenario": "general",
  "persona": "city_console",
  "total": 20
}
```

**Example**:
```bash
# Top 10 properties for daycare scenario with minimum score 5.0
curl "http://localhost:8000/api/scores/ranked?scenario=daycare&limit=10&min_score=5.0"
```

---

## Compare

### `POST /api/compare`

Compare up to 3 properties side-by-side with their scores.

**Request Body**:
```json
{
  "property_ids": [1, 5, 12],
  "scenario": "general",
  "persona": "city_console"
}
```

**Response**: `CompareResponse`

```json
{
  "items": [
    {
      "property": { "...PropertyResponse..." },
      "scores": { "...ScoreDetail..." }
    },
    {
      "property": { "...PropertyResponse..." },
      "scores": { "...ScoreDetail..." }
    }
  ],
  "scenario": "general",
  "persona": "city_console"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"property_ids": [1, 5, 12], "scenario": "grocery", "persona": "entrepreneur"}'
```

---

## Watchlist

### `GET /api/watchlist`

Get all watchlist items, optionally filtered by persona.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `persona` | string | — | Filter by persona (city_console or entrepreneur) |

**Response**: `WatchlistResponse`

```json
{
  "items": [
    {
      "id": 1,
      "property_id": 5,
      "persona": "city_console",
      "notes": "Great location for clinic",
      "created_at": "2026-03-06T10:00:00",
      "property": { "...PropertyResponse..." }
    }
  ],
  "total": 1
}
```

**Example**:
```bash
curl "http://localhost:8000/api/watchlist?persona=entrepreneur"
```

---

### `POST /api/watchlist`

Add a property to the watchlist.

**Request Body**:
```json
{
  "property_id": 5,
  "persona": "city_console",
  "notes": "Great location for clinic"
}
```

**Response** (201): `WatchlistItemResponse`

**Example**:
```bash
curl -X POST http://localhost:8000/api/watchlist \
  -H "Content-Type: application/json" \
  -d '{"property_id": 5, "persona": "city_console", "notes": "Great location for clinic"}'
```

---

### `DELETE /api/watchlist/{watchlist_id}`

Remove an item from the watchlist.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `watchlist_id` | int | Watchlist item ID |

**Response**: 204 No Content

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/watchlist/1
```

---

## Export

### `GET /api/export/csv`

Export the ranked property list as a CSV file download.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenario` | string | `"general"` | Scoring scenario |
| `persona` | string | `"city_console"` | User persona |

**Response**: CSV file download (`text/csv`)

CSV columns: `rank, property_id, parcel_id, address, neighborhood, overall_score,
foot_traffic, competition, safety, equity, activity, scenario`

**Example**:
```bash
curl "http://localhost:8000/api/export/csv?scenario=grocery" -o urbanpulse_export.csv
```

---

## Bright Data

### `GET /api/brightdata/signals/{property_id}`

Get or fetch web signals for a property. Returns cached data if available,
otherwise fetches fresh data from Bright Data (or simulated).

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | int | Property ID |

**Response**:
```json
{
  "property_id": 1,
  "poi_count": 15,
  "avg_rating": 3.8,
  "review_count": 87,
  "competitor_count": 4,
  "activity_index": 6.2,
  "source": "brightdata",
  "cached": true
}
```

**Example**:
```bash
curl http://localhost:8000/api/brightdata/signals/1
```

---

### `POST /api/brightdata/refresh/{property_id}`

Force refresh web signals for a property (deletes cached data and re-fetches).

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `property_id` | int | Property ID |

**Response**:
```json
{
  "property_id": 1,
  "poi_count": 18,
  "avg_rating": 4.0,
  "review_count": 92,
  "competitor_count": 3,
  "refreshed": true
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/brightdata/refresh/1
```

---

### `POST /api/brightdata/seed-all`

Fetch and cache web signals for all properties in the database.

**Response**:
```json
{
  "seeded": 50,
  "results": [
    {"property_id": 1, "activity_index": 6.2},
    {"property_id": 2, "activity_index": 5.8}
  ]
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/brightdata/seed-all
```

---

### `GET /api/brightdata/status`

Check Bright Data configuration status.

**Response**:
```json
{
  "configured": false,
  "base_url": "https://api.brightdata.com",
  "mode": "simulated"
}
```

**Example**:
```bash
curl http://localhost:8000/api/brightdata/status
```

---

## Agent (AI Copilot)

### `POST /api/agent/ask`

Ask the UrbanPulse AI copilot a natural-language question. The orchestrator
coordinates specialist lens agents (Equity, Risk, BizCoach) and returns
a comprehensive answer with property recommendations.

**Request Body**:
```json
{
  "query": "Where should I open a grocery store in Montgomery?",
  "persona": "entrepreneur",
  "scenario": "grocery"
}
```

**Response**:
```json
{
  "answer": "Based on my analysis of Montgomery's property data...",
  "recommended_properties": [
    {
      "id": 5,
      "address": "200 Perry St",
      "neighborhood": "Capitol Heights",
      "property_type": "commercial",
      "score": {
        "overall_score": 8.5,
        "equity_score": 9.2,
        "foot_traffic_score": 7.0
      }
    }
  ],
  "lens_outputs": {
    "equity": "Capitol Heights is underserved for grocery...",
    "risk": "Safety score is favorable at 8.2...",
    "bizcoach": "The competitive landscape shows an opportunity..."
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the safest areas for a daycare?", "persona": "entrepreneur", "scenario": "daycare"}'
```

---

### `POST /api/agent/story`

Generate a narrative city tour for a given scenario. Returns a guided walkthrough
of the top-scoring areas with storytelling context.

**Request Body**:
```json
{
  "scenario": "general",
  "persona": "city_console"
}
```

**Response**:
```json
{
  "story": "# City Tour: Montgomery's Top Opportunities\n\nWelcome to Montgomery...",
  "featured_properties": [ ... ]
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/agent/story \
  -H "Content-Type: application/json" \
  -d '{"scenario": "grocery", "persona": "city_console"}'
```

---

## Common Schemas

### PropertyResponse

```json
{
  "id": "int",
  "parcel_id": "string",
  "address": "string",
  "latitude": "float",
  "longitude": "float",
  "property_type": "string (residential|commercial|mixed|vacant_land)",
  "zoning": "string | null",
  "is_vacant": "bool",
  "is_city_owned": "bool",
  "lot_size_sqft": "float | null",
  "building_sqft": "float | null",
  "assessed_value": "float | null",
  "year_built": "int | null",
  "neighborhood": "string | null",
  "council_district": "string | null",
  "score": "ScoreDetail | null"
}
```

### ScoreDetail

```json
{
  "foot_traffic_score": "float (0-10)",
  "competition_score": "float (0-10)",
  "safety_score": "float (0-10)",
  "equity_score": "float (0-10)",
  "activity_index": "float (0-10)",
  "overall_score": "float (0-10)",
  "scenario": "string",
  "computed_at": "datetime | null"
}
```

### Scenarios

| Value | Description |
|-------|-------------|
| `general` | Default balanced scoring |
| `grocery` | Grocery store siting (equity-heavy) |
| `clinic` | Healthcare clinic (equity-heavy) |
| `daycare` | Childcare center (safety-heavy) |
| `coworking` | Coworking space (foot-traffic & activity-heavy) |

### Personas

| Value | Description |
|-------|-------------|
| `city_console` | City planner / public sector |
| `entrepreneur` | Business owner / investor |
