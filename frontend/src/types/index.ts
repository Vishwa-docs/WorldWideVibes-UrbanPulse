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
  median_age?: number;
  housing: DemographicsHousing;
  race: Record<string, number>;
  economics: DemographicsEconomics;
  education?: {
    total_25plus: number | null;
    high_school: number | null;
    bachelors: number | null;
    masters: number | null;
    doctorate: number | null;
    bachelors_plus_pct: number | null;
  };
  commuting?: {
    total: number | null;
    commute_total: number | null;
    drove_alone: number | null;
    public_transit: number | null;
    walked: number | null;
    work_from_home: number | null;
    drove_alone_pct: number | null;
    public_transit_pct: number | null;
    work_from_home_pct: number | null;
  };
  transportation?: {
    zero_vehicle_households: number | null;
    total_vehicle_households: number | null;
    zero_vehicle_pct: number | null;
  };
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
export type MapLayerType = 'vacant' | 'city_owned' | 'incidents' | 'business_clusters' | 'equity_overlay' | 'city_projects' | 'demographics' | 'service_requests' | 'foot_traffic' | 'vacant_reports' | 'business_licenses' | 'code_violations' | 'opportunity_zones' | 'city_owned_properties' | 'building_permits';

export interface MapLayer {
  id: MapLayerType;
  label: string;
  enabled: boolean;
  color: string;
}

// ── Weather ────────────────────────────────────────────────────────────
export interface WeatherCurrent {
  location: string;
  temperature_f: number;
  feels_like_f: number;
  humidity_pct: number;
  precipitation_in: number;
  wind_speed_mph: number;
  wind_direction: number;
  weather_code: number;
  weather_description: string;
  source: string;
  is_live: boolean;
  fetched_at: string;
}

export interface WeatherForecastDay {
  date: string;
  high_f: number;
  low_f: number;
  precipitation_in: number;
  wind_max_mph: number;
  weather_code: number;
  weather_description: string;
}

export interface WeatherForecast {
  location: string;
  forecast: WeatherForecastDay[];
  source: string;
  is_live: boolean;
  fetched_at: string;
}

// ── Montgomery Open Data ───────────────────────────────────────────────
export interface CodeViolation {
  id: number | null;
  case_number: string;
  violation_type: string;
  description: string;
  address: string;
  status: string;
  latitude: number;
  longitude: number;
  date_reported: string | null;
  source: string;
}

export interface OpportunityZone {
  id: number | null;
  zone_id: string;
  name: string;
  designation: string;
  latitude: number;
  longitude: number;
  source: string;
}

export interface CityOwnedProperty {
  id: number | null;
  parcel_id: string;
  address: string;
  property_type: string;
  acreage: number | null;
  latitude: number;
  longitude: number;
  source: string;
}

export interface BuildingPermit {
  id: number | null;
  permit_number: string;
  permit_type: string;
  description: string;
  address: string;
  status: string;
  latitude: number;
  longitude: number;
  issue_date: string | null;
  source: string;
}

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

// ── Workforce Copilot ───────────────────────────────────────────────────────
export type OpportunityRole = 'resident' | 'entrepreneur' | 'city' | 'education';

export interface ProvenanceSource {
  id: string;
  label: string;
  source_type: string;
  is_live: boolean;
  observed_at?: string | null;
  confidence: number;
  url?: string;
  note?: string;
}

export interface OpportunityScorecard {
  resident_fit_score: number;
  business_opportunity_score: number;
  city_impact_score: number;
  overall_score: number;
}

export interface OpportunityRecommendation {
  rank: number;
  property: Property;
  scores: OpportunityScorecard;
  top_factors: string[];
  evidence_ids: string[];
}

export interface OpportunitiesOverviewResponse {
  role: OpportunityRole;
  scenario: ScenarioType;
  total_properties: number;
  role_focus: string;
  kpis: Record<string, number | string>;
  top_recommendations: OpportunityRecommendation[];
  sources: ProvenanceSource[];
  generated_at: string;
  confidence: number;
}

export interface RecommendationQueryRequest {
  query: string;
  role: OpportunityRole;
  scenario: ScenarioType;
  limit?: number;
  refresh_live?: boolean;
  property_ids?: number[];
}

export interface RecommendationQueryResponse {
  recommendation_id: string;
  role: OpportunityRole;
  scenario: ScenarioType;
  query: string;
  summary: string;
  recommendations: OpportunityRecommendation[];
  sources: ProvenanceSource[];
  generated_at: string;
  confidence: number;
}

export interface EvidenceResponse {
  recommendation_id: string;
  evidence: ProvenanceSource[];
  generated_at: string;
}

export interface SignalRefreshItem {
  property_id: number;
  address: string;
  activity_index: number;
  is_live: boolean;
  source: string;
  fetched_at: string;
}

export interface SignalsRefreshResponse {
  refreshed_count: number;
  mode: string;
  items: SignalRefreshItem[];
  sources: ProvenanceSource[];
  generated_at: string;
}

export interface SignalChangeItem {
  property_id: number;
  address: string;
  previous_activity_index: number;
  current_activity_index: number;
  delta_activity_index: number;
  previous_fetched_at?: string;
  current_fetched_at?: string;
}

export interface SignalChangesResponse {
  window_hours: number;
  changes: SignalChangeItem[];
  generated_at: string;
  sources: ProvenanceSource[];
}

// ── Bright Data SERP & Scrape ───────────────────────────────────────────

export interface SerpResult {
  title: string;
  url: string;
  description: string;
  position: number;
}

export interface SerpResponse {
  query: string;
  engine: string;
  location: string;
  result_count: number;
  results: SerpResult[];
  source: string;
  is_live: boolean;
  fetched_at: string;
  error?: string;
}

export interface ScrapeResponse {
  url: string;
  content: string;
  content_length: number;
  source: string;
  is_live: boolean;
  fetched_at: string;
  error?: string;
}

export interface BrightDataProduct {
  name: string;
  description: string;
  endpoint: string;
  status: string;
  methods: string[];
}

export interface BrightDataCapabilities {
  products: BrightDataProduct[];
  configured: boolean;
  mode: string;
}
