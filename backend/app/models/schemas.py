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
    ai_narrative: str = ""


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


# ── Workforce / Opportunity Copilot ─────────────────────────────────────────

class ProvenanceSource(BaseModel):
    """Source metadata attached to insights and recommendations."""
    id: str
    label: str
    source_type: str
    is_live: bool = False
    observed_at: Optional[datetime] = None
    confidence: float = 0.5
    url: Optional[str] = None
    note: Optional[str] = None


class OpportunityScorecard(BaseModel):
    """Role-specific score bundle for a property opportunity."""
    resident_fit_score: float
    business_opportunity_score: float
    city_impact_score: float
    overall_score: float


class OpportunityRecommendation(BaseModel):
    """One ranked recommendation in query output."""
    rank: int
    property: PropertyResponse
    scores: OpportunityScorecard
    top_factors: list[str] = []
    evidence_ids: list[str] = []


class OpportunitiesOverviewResponse(BaseModel):
    """High-level dashboard summary for a role/scenario."""
    role: str
    scenario: str
    total_properties: int
    role_focus: str
    kpis: dict[str, float | int | str]
    top_recommendations: list[OpportunityRecommendation] = []
    sources: list[ProvenanceSource] = []
    generated_at: datetime
    confidence: float


class RecommendationQueryRequest(BaseModel):
    """Structured recommendation query request."""
    query: str = ""
    role: str = "resident"
    scenario: str = "general"
    limit: int = Field(default=5, ge=1, le=20)
    refresh_live: bool = False
    property_ids: Optional[list[int]] = None


class RecommendationQueryResponse(BaseModel):
    """Structured recommendation query response."""
    recommendation_id: str
    role: str
    scenario: str
    query: str
    summary: str
    recommendations: list[OpportunityRecommendation]
    sources: list[ProvenanceSource]
    generated_at: datetime
    confidence: float


class EvidenceResponse(BaseModel):
    """Evidence cards for a generated recommendation set."""
    recommendation_id: str
    evidence: list[ProvenanceSource]
    generated_at: datetime


class SignalsRefreshRequest(BaseModel):
    """Signal refresh request."""
    property_ids: Optional[list[int]] = None
    force_live: bool = False
    limit: int = Field(default=50, ge=1, le=300)


class SignalRefreshItem(BaseModel):
    """Per-property signal refresh status."""
    property_id: int
    address: str
    activity_index: float
    is_live: bool
    source: str
    fetched_at: datetime


class SignalsRefreshResponse(BaseModel):
    """Bulk signal refresh response."""
    refreshed_count: int
    mode: str
    items: list[SignalRefreshItem]
    sources: list[ProvenanceSource]
    generated_at: datetime


class SignalChangeItem(BaseModel):
    """Delta between current and previous signal snapshots."""
    property_id: int
    address: str
    previous_activity_index: float
    current_activity_index: float
    delta_activity_index: float
    previous_fetched_at: Optional[datetime] = None
    current_fetched_at: Optional[datetime] = None


class SignalChangesResponse(BaseModel):
    """Signal change feed showing activity deltas over a time window."""
    window_hours: int
    changes: list[SignalChangeItem]
    generated_at: datetime
    sources: list[ProvenanceSource]
