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
  window.open(`/api/export/csv?${params}`, '_blank');
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

export default api;
