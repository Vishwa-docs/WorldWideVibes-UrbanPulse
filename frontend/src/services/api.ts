import axios from 'axios';
import type {
  Property,
  ScorecardResponse,
  RankedListResponse,
  CompareResponse,
  WatchlistResponse,
  WatchlistItem,
  PersonaType,
  ScenarioType,
  AgentResponse,
  StoryResponse,
  WalkScoreResponse,
  DemographicsResponse,
  SiteReportResponse,
  MarketGapResponse,
  InvestmentAnalysisResponse,
  ServiceRequest311,
  MostVisitedLocation,
  VisitorOrigin,
  BusinessLicense,
  VacantPropertyReport,
  WorkforceData,
  DataSourcesSummary,
  OpportunityRole,
  OpportunitiesOverviewResponse,
  RecommendationQueryRequest,
  RecommendationQueryResponse,
  EvidenceResponse,
  SignalsRefreshResponse,
  SignalChangesResponse,
  SerpResponse,
  ScrapeResponse,
  BrightDataCapabilities,
  CodeViolation,
  OpportunityZone,
  CityOwnedProperty,
  BuildingPermit,
  WeatherCurrent,
  WeatherForecast,
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: { 'Content-Type': 'application/json' },
});

// ── Health ──────────────────────────────────────────────────────────────
export const healthCheck = () => api.get('/api/health').then(r => r.data);

// ── Properties ──────────────────────────────────────────────────────────
export const fetchProperties = (params?: {
  is_vacant?: boolean;
  is_city_owned?: boolean;
  neighborhood?: string;
  property_type?: string;
  skip?: number;
  limit?: number;
}) => api.get<Property[]>('/api/properties', { params }).then(r => r.data);

export const fetchProperty = (id: number) =>
  api.get<Property>(`/api/properties/${id}`).then(r => r.data);

export const fetchScorecard = (id: number) =>
  api.get<ScorecardResponse>(`/api/properties/${id}/scorecard`).then(r => r.data);

// ── Scores ──────────────────────────────────────────────────────────────
export const computeScores = (scenario: ScenarioType, persona: PersonaType) =>
  api.post('/api/scores/compute', { scenario, persona }).then(r => r.data);

export const fetchRankedList = (params: {
  scenario?: ScenarioType;
  persona?: PersonaType;
  limit?: number;
  min_score?: number;
}) => api.get<RankedListResponse>('/api/scores/ranked', { params }).then(r => r.data);

// ── Compare ─────────────────────────────────────────────────────────────
export const compareProperties = (
  property_ids: number[],
  scenario: ScenarioType,
  persona: PersonaType,
) => api.post<CompareResponse>('/api/compare', { property_ids, scenario, persona }).then(r => r.data);

// ── Watchlist ───────────────────────────────────────────────────────────
export const fetchWatchlist = (persona?: PersonaType) =>
  api.get<WatchlistResponse>('/api/watchlist', { params: { persona } }).then(r => r.data);

export const addToWatchlist = (property_id: number, persona: PersonaType, notes?: string) =>
  api.post<WatchlistItem>('/api/watchlist', { property_id, persona, notes }).then(r => r.data);

export const removeFromWatchlist = (id: number) =>
  api.delete(`/api/watchlist/${id}`).then(r => r.data);

// ── Export ──────────────────────────────────────────────────────────────
export const exportCSV = (scenario: ScenarioType, persona: PersonaType) => {
  const params = new URLSearchParams({ scenario, persona });
  const base = (api.defaults.baseURL || '').replace(/\/$/, '');
  const url = `${base}/api/export/csv?${params}`;
  window.open(url, '_blank');
};

// ── Agent / AI ──────────────────────────────────────────────────────────
export const askAgent = (query: string, persona: PersonaType, scenario: ScenarioType) =>
  api.post<AgentResponse>('/api/agent/ask', { query, persona, scenario }).then(r => r.data);

export const fetchStory = (scenario: ScenarioType, persona: PersonaType) =>
  api.post<StoryResponse>('/api/agent/story', { scenario, persona }).then(r => r.data);

// ── Walk Score ──────────────────────────────────────────────────────────
export const fetchWalkScore = (propertyId: number) =>
  api.get<WalkScoreResponse>(`/api/walkscore/${propertyId}`).then(r => r.data);

export const fetchWalkScoreByCoords = (lat: number, lng: number) =>
  api.get<WalkScoreResponse>('/api/walkscore/coordinates/', { params: { lat, lng } }).then(r => r.data);

// ── Demographics ────────────────────────────────────────────────────────
export const fetchTractDemographics = (lat: number, lng: number) =>
  api.get<DemographicsResponse>('/api/demographics/tract', { params: { lat, lng } }).then(r => r.data);

export const fetchCityDemographics = () =>
  api.get<DemographicsResponse>('/api/demographics/city').then(r => r.data);

// ── Insights ────────────────────────────────────────────────────────────
export const fetchSiteReport = (propertyId: number) =>
  api.get<SiteReportResponse>(`/api/insights/site-report/${propertyId}`).then(r => r.data);

export const fetchMarketGaps = (scenario?: ScenarioType) =>
  api.get<MarketGapResponse>('/api/insights/market-gaps', { params: { scenario } }).then(r => r.data);

export const fetchInvestmentAnalysis = (propertyId: number) =>
  api.get<InvestmentAnalysisResponse>(`/api/insights/investment-analysis/${propertyId}`).then(r => r.data);

// ── Montgomery Open Data ────────────────────────────────────────────────
export const fetch311Requests = (limit = 200, category?: string) =>
  api.get<{ items: ServiceRequest311[]; total: number }>('/api/montgomery/311', {
    params: { limit, ...(category ? { category } : {}) },
  }).then(r => r.data);

export const fetchMostVisited = (limit = 200) =>
  api.get<{ items: MostVisitedLocation[]; total: number }>('/api/montgomery/most-visited', {
    params: { limit },
  }).then(r => r.data);

export const fetchVisitorOrigin = (limit = 200) =>
  api.get<{ items: VisitorOrigin[]; total: number }>('/api/montgomery/visitor-origin', {
    params: { limit },
  }).then(r => r.data);

export const fetchBusinessLicenses = (limit = 200, businessType?: string) =>
  api.get<{ items: BusinessLicense[]; total: number }>('/api/montgomery/business-licenses', {
    params: { limit, ...(businessType ? { business_type: businessType } : {}) },
  }).then(r => r.data);

export const fetchVacantPropertyReports = (limit = 200) =>
  api.get<{ items: VacantPropertyReport[]; total: number }>('/api/montgomery/vacant-properties', {
    params: { limit },
  }).then(r => r.data);

// ── Workforce ───────────────────────────────────────────────────────────
export const fetchWorkforceData = () =>
  api.get<WorkforceData>('/api/montgomery/workforce').then(r => r.data);

// ── Data Sources ────────────────────────────────────────────────────────
export const fetchDataSources = () =>
  api.get<DataSourcesSummary>('/api/montgomery/data-sources').then(r => r.data);

// ── Workforce Copilot ───────────────────────────────────────────────────
export const fetchOpportunitiesOverview = (role: OpportunityRole, scenario: ScenarioType) =>
  api.get<OpportunitiesOverviewResponse>('/api/opportunities/overview', {
    params: { role, scenario },
  }).then(r => r.data);

export const queryRecommendations = (body: RecommendationQueryRequest) =>
  api.post<RecommendationQueryResponse>('/api/recommendations/query', body).then(r => r.data);

export const fetchEvidence = (recommendationId: string) =>
  api.get<EvidenceResponse>(`/api/evidence/${recommendationId}`).then(r => r.data);

export const refreshSignals = (params?: { property_ids?: number[]; force_live?: boolean; limit?: number }) =>
  api.post<SignalsRefreshResponse>('/api/signals/refresh', {
    property_ids: params?.property_ids,
    force_live: params?.force_live ?? false,
    limit: params?.limit ?? 50,
  }).then(r => r.data);

export const fetchSignalChanges = (windowHours = 24) =>
  api.get<SignalChangesResponse>('/api/signals/changes', {
    params: { window_hours: windowHours },
  }).then(r => r.data);

// ── Bright Data SERP & Scrape ───────────────────────────────────────────
export const searchSerp = (query: string, engine = 'google', numResults = 10) =>
  api.post<SerpResponse>('/api/brightdata/serp', {
    query,
    engine,
    location: 'Montgomery,Alabama,United States',
    num_results: numResults,
  }).then(r => r.data);

export const searchLocal = (q: string, category = 'business') =>
  api.get<SerpResponse>('/api/brightdata/serp/local', {
    params: { q, category },
  }).then(r => r.data);

export const scrapeUrl = (url: string, maxLength = 8000) =>
  api.post<ScrapeResponse>('/api/brightdata/scrape', {
    url,
    max_length: maxLength,
  }).then(r => r.data);

export const fetchBrightDataCapabilities = () =>
  api.get<BrightDataCapabilities>('/api/brightdata/capabilities').then(r => r.data);

// ── Montgomery Extended Data ────────────────────────────────────────────
export const fetchCodeViolations = (limit = 200, violationType?: string) =>
  api.get<{ items: CodeViolation[]; total: number }>('/api/montgomery/code-violations', {
    params: { limit, ...(violationType ? { violation_type: violationType } : {}) },
  }).then(r => r.data);

export const fetchOpportunityZones = (limit = 100) =>
  api.get<{ items: OpportunityZone[]; total: number }>('/api/montgomery/opportunity-zones', {
    params: { limit },
  }).then(r => r.data);

export const fetchCityOwnedProperties = (limit = 200) =>
  api.get<{ items: CityOwnedProperty[]; total: number }>('/api/montgomery/city-owned-properties', {
    params: { limit },
  }).then(r => r.data);

export const fetchBuildingPermits = (limit = 200, permitType?: string) =>
  api.get<{ items: BuildingPermit[]; total: number }>('/api/montgomery/building-permits', {
    params: { limit, ...(permitType ? { permit_type: permitType } : {}) },
  }).then(r => r.data);

// ── Weather ─────────────────────────────────────────────────────────────
export const fetchCurrentWeather = () =>
  api.get<WeatherCurrent>('/api/weather/current').then(r => r.data);

export const fetchWeatherForecast = () =>
  api.get<WeatherForecast>('/api/weather/forecast').then(r => r.data);

export default api;
