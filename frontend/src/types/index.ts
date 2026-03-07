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

// ── Walk Score ─────────────────────────────────────────────────────────
export interface WalkScoreCategoryBreakdown {
  count: number;
  raw_score: number;
  weighted_score: number;
}

export interface WalkScoreResponse {
  property_id?: number;
  address?: string;
  neighborhood?: string;
  latitude?: number;
  longitude?: number;
  walk_score: number;
  label: string;
  total_amenities_nearby: number;
  category_breakdown: Record<string, WalkScoreCategoryBreakdown>;
}

// ── Demographics ───────────────────────────────────────────────────────
export interface DemographicsHousing {
  total_units: number;
  owner_occupied: number;
  renter_occupied: number;
  vacant: number;
  owner_occupied_pct: number;
  renter_occupied_pct: number;
  vacancy_rate_pct: number;
}

export interface DemographicsEconomics {
  below_poverty_level: number;
  poverty_rate_pct: number;
  unemployed: number;
  in_labor_force: number;
  unemployment_rate_pct: number;
}

export interface DemographicsResponse {
  total_population: number;
  median_household_income: number;
  median_home_value: number;
  housing: DemographicsHousing;
  race: Record<string, number>;
  economics: DemographicsEconomics;
  commuters?: { total: number };
  place_name?: string;
  tract?: string;
}

// ── Insights ───────────────────────────────────────────────────────────
export interface SiteReportResponse {
  property_id: number;
  property_address: string;
  report: string;
  demographics: Record<string, unknown> | null;
  walk_score: WalkScoreResponse | null;
  generated_at: string;
}

export interface MarketGapResponse {
  scenario: string;
  analysis: string;
  service_distribution: Record<string, number>;
  total_properties: number;
  generated_at: string;
}

export interface InvestmentAnalysisResponse {
  property_id: number;
  property_address: string;
  analysis: string;
  scores: Record<string, number> | null;
  demographics: Record<string, unknown> | null;
  generated_at: string;
}

// ── Map Layers ─────────────────────────────────────────────────────────
export type MapLayerType = 'vacant' | 'city_owned' | 'incidents' | 'business_clusters' | 'equity_overlay' | 'city_projects' | 'demographics' | 'service_requests' | 'foot_traffic' | 'vacant_reports' | 'business_licenses';

export interface MapLayer {
  id: MapLayerType;
  label: string;
  enabled: boolean;
  color: string;
}

// ── Montgomery Open Data ───────────────────────────────────────────────
export interface ServiceRequest311 {
  id: number | null;
  category: string;
  description: string;
  status: string;
  address: string;
  latitude: number;
  longitude: number;
  created_date: string | null;
  source: string;
}

export interface MostVisitedLocation {
  id: number | null;
  name: string;
  category: string;
  visits: number;
  visitors: number;
  latitude: number;
  longitude: number;
  source: string;
}

export interface VisitorOrigin {
  id: number | null;
  origin: string;
  destination: string;
  visitor_count: number;
  latitude: number;
  longitude: number;
  source: string;
}

export interface BusinessLicense {
  id: number | null;
  business_name: string;
  business_type: string;
  address: string;
  status: string;
  latitude: number;
  longitude: number;
  source: string;
}

export interface VacantPropertyReport {
  id: number | null;
  category: string;
  description: string;
  address: string;
  status: string;
  latitude: number;
  longitude: number;
  source: string;
}

// ── Workforce ──────────────────────────────────────────────────────────
export interface WorkforceEmployment {
  population_16_plus: number;
  in_labor_force: number;
  employed: number;
  unemployed: number;
  not_in_labor_force: number;
  labor_force_participation_rate: number;
  unemployment_rate: number;
  employment_rate: number;
}

export interface WorkforceIndustry {
  industry: string;
  employed: number;
  percentage: number;
}

export interface WorkforceEducation {
  population_25_plus: number;
  high_school_diploma: number;
  associates_degree: number;
  bachelors_degree: number;
  graduate_degree: number;
  bachelors_or_higher_pct: number;
  hs_or_higher_pct: number;
}

export interface WorkforceCommuting {
  total_workers: number;
  drove_alone: number;
  carpooled: number;
  public_transit: number;
  walked: number;
  work_from_home: number;
  drove_alone_pct: number;
}

export interface WorkforceData {
  area: string;
  employment: WorkforceEmployment;
  industries: WorkforceIndustry[];
  education: WorkforceEducation;
  commuting: WorkforceCommuting;
  source: string;
}

// ── Data Sources ───────────────────────────────────────────────────────
export interface DataSourceInfo {
  available: boolean;
  source: string;
}

export interface DataSourcesSummary {
  sources: Record<string, DataSourceInfo>;
  total_sources: number;
}
