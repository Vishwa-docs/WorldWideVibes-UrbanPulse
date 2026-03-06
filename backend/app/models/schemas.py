"""Pydantic response/request schemas for UrbanPulse API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Score-related ─────────────────────────────────────────────────────────────

class ScoreDetail(BaseModel):
    """Breakdown of an individual property score."""
    foot_traffic_score: float = 0.0
    competition_score: float = 0.0
    safety_score: float = 0.0
    equity_score: float = 0.0
    activity_index: float = 0.0
    overall_score: float = 0.0
    scenario: str = "general"
    computed_at: Optional[datetime] = None


# ── Property responses ────────────────────────────────────────────────────────

class PropertyResponse(BaseModel):
    """Property with its latest scores."""
    id: int
    parcel_id: str
    address: str
    latitude: float
    longitude: float
    property_type: str
    zoning: Optional[str] = None
    is_vacant: bool
    is_city_owned: bool
    lot_size_sqft: Optional[float] = None
    building_sqft: Optional[float] = None
    assessed_value: Optional[float] = None
    year_built: Optional[int] = None
    neighborhood: Optional[str] = None
    council_district: Optional[str] = None
    score: Optional[ScoreDetail] = None


class IncidentNearby(BaseModel):
    """Abbreviated incident for scorecard."""
    id: int
    incident_type: str
    latitude: float
    longitude: float
    severity: Optional[str] = None
    distance_km: Optional[float] = None


class ServiceNearby(BaseModel):
    """Abbreviated service location for scorecard."""
    id: int
    name: str
    service_type: str
    latitude: float
    longitude: float
    distance_km: Optional[float] = None


class ScorecardResponse(BaseModel):
    """Full scorecard for a single property."""
    property: PropertyResponse
    scores: ScoreDetail
    nearby_incidents: list[IncidentNearby] = []
    nearby_services: list[ServiceNearby] = []
    ai_narrative: str = "AI narrative placeholder – connect Gemini for real insights."


# ── Compare ───────────────────────────────────────────────────────────────────

class ComparePropertyItem(BaseModel):
    """One property in a comparison result."""
    property: PropertyResponse
    scores: ScoreDetail


class CompareRequest(BaseModel):
    """Request body for comparing properties."""
    property_ids: list[int] = Field(..., min_length=1, max_length=3)
    scenario: str = "general"
    persona: str = "city_console"


class CompareResponse(BaseModel):
    """Side-by-side comparison of multiple properties."""
    items: list[ComparePropertyItem]
    scenario: str
    persona: str


# ── Score compute ─────────────────────────────────────────────────────────────

class ScoreComputeRequest(BaseModel):
    """Request body for recomputing scores."""
    scenario: str = "general"
    persona: str = "city_console"


class ScoreComputeResponse(BaseModel):
    """Result of a batch score computation."""
    computed_count: int
    scenario: str
    persona: str


# ── Ranked list ───────────────────────────────────────────────────────────────

class RankedPropertyItem(BaseModel):
    """A property with its rank and score."""
    rank: int
    property: PropertyResponse
    overall_score: float


class RankedListResponse(BaseModel):
    """Ranked list of properties by overall score."""
    items: list[RankedPropertyItem]
    scenario: str
    persona: str
    total: int


# ── Watchlist ─────────────────────────────────────────────────────────────────

class WatchlistRequest(BaseModel):
    """Request body for adding to the watchlist."""
    property_id: int
    persona: str = "city_console"
    notes: Optional[str] = None


class WatchlistItemResponse(BaseModel):
    """Single watchlist item."""
    id: int
    property_id: int
    persona: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    property: Optional[PropertyResponse] = None


class WatchlistResponse(BaseModel):
    """List of watchlist items."""
    items: list[WatchlistItemResponse]
    total: int
