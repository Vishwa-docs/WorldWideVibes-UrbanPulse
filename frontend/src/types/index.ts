// ── Persona ────────────────────────────────────────────────────────────
export type PersonaType = 'city_console' | 'entrepreneur';

export interface Persona {
  type: PersonaType;
  label: string;
  description: string;
  icon: string;
}

// ── Scenario ───────────────────────────────────────────────────────────
export type ScenarioType = 'general' | 'grocery' | 'clinic' | 'daycare' | 'coworking';

export interface Scenario {
  id: ScenarioType;
  name: string;
  description: string;
  icon: string;
}

// ── Scores ─────────────────────────────────────────────────────────────
export interface ScoreDetail {
  foot_traffic_score: number;
  competition_score: number;
  safety_score: number;
  equity_score: number;
  activity_index: number;
  overall_score: number;
  scenario: string;
  computed_at?: string;
}

// ── Property ───────────────────────────────────────────────────────────
export interface Property {
  id: number;
  parcel_id: string;
  address: string;
  latitude: number;
  longitude: number;
  property_type: string;
  zoning?: string;
  is_vacant: boolean;
  is_city_owned: boolean;
  lot_size_sqft?: number;
  building_sqft?: number;
  assessed_value?: number;
  year_built?: number;
  neighborhood?: string;
  council_district?: string;
  score?: ScoreDetail;
}

// ── Scorecard ──────────────────────────────────────────────────────────
export interface IncidentNearby {
  id: number;
  incident_type: string;
  latitude: number;
  longitude: number;
  severity?: string;
  distance_km?: number;
}

export interface ServiceNearby {
  id: number;
  name: string;
  service_type: string;
  latitude: number;
  longitude: number;
  distance_km?: number;
}

export interface ScorecardResponse {
  property: Property;
  scores: ScoreDetail;
  nearby_incidents: IncidentNearby[];
  nearby_services: ServiceNearby[];
  ai_narrative: string;
}

// ── Compare ────────────────────────────────────────────────────────────
export interface ComparePropertyItem {
  property: Property;
  scores: ScoreDetail;
}

export interface CompareResponse {
  items: ComparePropertyItem[];
  scenario: string;
  persona: string;
}

// ── Ranked ─────────────────────────────────────────────────────────────
export interface RankedPropertyItem {
  rank: number;
  property: Property;
  overall_score: number;
}

export interface RankedListResponse {
  items: RankedPropertyItem[];
  scenario: string;
  persona: string;
  total: number;
}

// ── Watchlist ──────────────────────────────────────────────────────────
export interface WatchlistItem {
  id: number;
  property_id: number;
  persona: string;
  notes?: string;
  created_at?: string;
  property?: Property;
}

export interface WatchlistResponse {
  items: WatchlistItem[];
  total: number;
}

// ── Agent / AI ─────────────────────────────────────────────────────────
export interface AgentQuery {
  query: string;
  persona: PersonaType;
  scenario: ScenarioType;
}

export interface AgentResponse {
  answer: string;
  recommended_properties?: Property[];
  lens_outputs?: {
    equity?: string;
    risk?: string;
    bizcoach?: string;
  };
}

export interface StoryResponse {
  title: string;
  narrative: string;
  properties: Property[];
}

// ── Map Layers ─────────────────────────────────────────────────────────
export type MapLayerType = 'vacant' | 'city_owned' | 'incidents' | 'business_clusters' | 'equity_overlay' | 'city_projects';

export interface MapLayer {
  id: MapLayerType;
  label: string;
  enabled: boolean;
  color: string;
}
