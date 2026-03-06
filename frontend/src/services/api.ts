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

export default api;
