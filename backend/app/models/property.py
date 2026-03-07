"""Property and related data models for UrbanPulse."""
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class Property(SQLModel, table=True):
    """Core property/parcel record from Montgomery open data."""
    __tablename__ = "properties"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    parcel_id: str = Field(index=True, unique=True)
    address: str = Field(index=True)
    latitude: float
    longitude: float
    property_type: str = Field(default="unknown")  # residential, commercial, mixed, vacant_land
    zoning: Optional[str] = None
    is_vacant: bool = Field(default=False)
    is_city_owned: bool = Field(default=False)
    lot_size_sqft: Optional[float] = None
    building_sqft: Optional[float] = None
    assessed_value: Optional[float] = None
    year_built: Optional[int] = None
    neighborhood: Optional[str] = None
    council_district: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PropertyScore(SQLModel, table=True):
    """Computed scores for a property under a given scenario."""
    __tablename__ = "property_scores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="properties.id", index=True)
    scenario: str = Field(default="general")  # general, grocery, clinic, daycare, coworking
    overall_score: float = Field(default=0.0)
    foot_traffic_score: float = Field(default=0.0)
    competition_score: float = Field(default=0.0)
    safety_score: float = Field(default=0.0)
    equity_score: float = Field(default=0.0)
    activity_index: float = Field(default=0.0)
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class WebSignal(SQLModel, table=True):
    """Web-scraped signals from Bright Data for a property's area."""
    __tablename__ = "web_signals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="properties.id", index=True)
    poi_count: int = Field(default=0)
    avg_rating: Optional[float] = None
    review_count: int = Field(default=0)
    competitor_count: int = Field(default=0)
    category: Optional[str] = None  # What was searched (restaurants, grocery, etc.)
    source: str = Field(default="brightdata")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class SignalSnapshot(SQLModel, table=True):
    """Historical signal snapshot used for delta/change tracking."""
    __tablename__ = "signal_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="properties.id", index=True)
    poi_count: int = Field(default=0)
    avg_rating: Optional[float] = None
    review_count: int = Field(default=0)
    competitor_count: int = Field(default=0)
    activity_index: float = Field(default=0.0)
    source: str = Field(default="brightdata")
    is_live: bool = Field(default=False)
    fetched_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Incident(SQLModel, table=True):
    """Safety/incident records from Montgomery open data."""
    __tablename__ = "incidents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    incident_id: Optional[str] = None
    incident_type: str = Field(default="unknown")
    latitude: float
    longitude: float
    reported_at: Optional[datetime] = None
    neighborhood: Optional[str] = None
    severity: Optional[str] = None  # low, medium, high


class ServiceLocation(SQLModel, table=True):
    """Locations of key services (groceries, clinics, parks, etc.)."""
    __tablename__ = "service_locations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    service_type: str  # grocery, clinic, park, school, daycare, library
    latitude: float
    longitude: float
    address: Optional[str] = None
    neighborhood: Optional[str] = None


class CityProject(SQLModel, table=True):
    """City infrastructure projects."""
    __tablename__ = "city_projects"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_name: str
    project_type: Optional[str] = None  # streetscape, infrastructure, park, transit
    status: str = Field(default="planned")  # planned, ongoing, completed
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    budget: Optional[float] = None
    description: Optional[str] = None


class Watchlist(SQLModel, table=True):
    """User watchlist items."""
    __tablename__ = "watchlists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    property_id: int = Field(foreign_key="properties.id", index=True)
    persona: str = Field(default="city_console")  # city_console, entrepreneur
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
