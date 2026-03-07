import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  ArrowRight,
  Briefcase,
  Building2,
  GraduationCap,
  Loader2,
  Map,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
  Users,
} from 'lucide-react';

import ScenarioSelector from '../components/Scenario/ScenarioSelector';
import { useScenario } from '../hooks/useScenario';
import { useAppState } from '../context/AppStateContext';
import {
  healthCheck,
  fetchOpportunitiesOverview,
  fetchSignalChanges,
  queryRecommendations,
  refreshSignals,
} from '../services/api';
import type {
  OpportunityRecommendation,
  OpportunityRole,
  OpportunitiesOverviewResponse,
  PersonaType,
  RecommendationQueryResponse,
  SignalChangesResponse,
} from '../types';

interface CopilotProps {
  activePersona: PersonaType;
}

const ROLE_TABS: { id: OpportunityRole; label: string; icon: typeof Users; blurb: string }[] = [
  { id: 'resident', label: 'Residents', icon: Users, blurb: 'Career paths, skills gaps & training.' },
  { id: 'entrepreneur', label: 'Entrepreneurs', icon: Briefcase, blurb: 'Demand, competition & locations.' },
  { id: 'city', label: 'City Staff', icon: Building2, blurb: 'Corridor priorities & action queue.' },
  { id: 'education', label: 'Education', icon: GraduationCap, blurb: 'Training aligned to live demand.' },
];

function scoreClass(v: number): string {
  if (v >= 7) return 'text-emerald-700 bg-emerald-50 border-emerald-200';
  if (v >= 4) return 'text-amber-700 bg-amber-50 border-amber-200';
  return 'text-rose-700 bg-rose-50 border-rose-200';
}

function roleQuery(role: OpportunityRole): string {
  const defaults: Record<OpportunityRole, string> = {
    resident: 'Find high-fit job growth zones with nearby training support',
    entrepreneur: 'Best grocery opportunity near underserved neighborhoods',
    city: 'Which vacant sites can deliver fastest city impact?',
    education: 'Which training programs match local hiring signals?',
  };
  return defaults[role] ?? 'Show top opportunities';
}

export default function Copilot(_props: CopilotProps) {
  const { activeScenario, selectScenario } = useScenario();
  const { activeRole, setActiveRole } = useAppState();

  const [overview, setOverview] = useState<OpportunitiesOverviewResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationQueryResponse | null>(null);
  const [changes, setChanges] = useState<SignalChangesResponse | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [refreshingSignals, setRefreshingSignals] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'checking' | 'ok' | 'down'>('checking');

  const checkApi = useCallback(async () => {
    try {
      await healthCheck();
      setApiStatus('ok');
      return true;
    } catch {
      setApiStatus('down');
      return false;
    }
  }, []);

  useEffect(() => {
    void checkApi();
  }, [checkApi]);

  useEffect(() => {
    if (apiStatus !== 'down') return;
    const timer = window.setInterval(() => { void checkApi(); }, 8000);
    return () => window.clearInterval(timer);
  }, [apiStatus, checkApi]);

  useEffect(() => {
    let cancelled = false;
    setLoadingOverview(true);
    setError(null);
    (async () => {
      try {
        const [overviewRes, recRes] = await Promise.all([
          fetchOpportunitiesOverview(activeRole, activeScenario),
          queryRecommendations({
            query: roleQuery(activeRole),
            role: activeRole,
            scenario: activeScenario,
            limit: 5,
          }),
        ]);
        if (!cancelled) {
          setOverview(overviewRes);
          setRecommendation(recRes);
          setApiStatus('ok');
        }
      } catch {
        if (cancelled) return;
        try {
          const fallback = await queryRecommendations({
            query: roleQuery(activeRole),
            role: activeRole,
            scenario: activeScenario,
            limit: 3,
          });
          if (!cancelled) {
            setRecommendation(fallback);
            setApiStatus('ok');
          }
        } catch {
          if (!cancelled) {
            setApiStatus('down');
            setError('Unable to load opportunity data. Please ensure the backend is running.');
          }
        }
      } finally {
        if (!cancelled) setLoadingOverview(false);
      }
    })();
    return () => { cancelled = true; };
  }, [activeRole, activeScenario]);

  useEffect(() => {
    fetchSignalChanges(48)
      .then(setChanges)
      .catch(() => {});
  }, []);

  const displayedRecommendations: OpportunityRecommendation[] = useMemo(() => {
    if (recommendation?.recommendations?.length) return recommendation.recommendations;
    return overview?.top_recommendations ?? [];
  }, [recommendation, overview]);

  const onRefreshSignals = async () => {
    setRefreshingSignals(true);
    try {
      await refreshSignals({ force_live: true, limit: 40 });
      const [nextOverview, nextChanges] = await Promise.all([
        fetchOpportunitiesOverview(activeRole, activeScenario),
        fetchSignalChanges(48),
      ]);
      setOverview(nextOverview);
      setChanges(nextChanges);
      setApiStatus('ok');
    } catch {
      setError('Signal refresh failed. Please try again.');
    } finally {
      setRefreshingSignals(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gradient-to-br from-slate-50 via-white to-indigo-50/30">
      <div className="max-w-7xl mx-auto px-5 md:px-8 py-6 space-y-5">
        {/* Hero Section */}
        <section className="rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-6 md:p-8 shadow-xl text-white relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyem0wLTMwVjBoMnYxMGgtMnptLTYgMGgydjEwaC0yVjR6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-50" />
          <div className="relative z-10 flex items-start justify-between gap-4 flex-wrap">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="h-1 w-8 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full" />
                <span className="text-xs uppercase tracking-[0.2em] text-indigo-300 font-semibold">Montgomery, AL — Workforce & Economic Growth</span>
              </div>
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
                UrbanPulse Opportunity Copilot
              </h1>
              <p className="mt-2 text-indigo-200 max-w-2xl text-sm leading-relaxed">
                Find the best locations for new businesses, jobs, and services in Montgomery.
                UrbanPulse analyzes <strong className="text-white">real-time city open data</strong> (zoning, parcels, demographics) and <strong className="text-white">Bright Data web signals</strong> (Google Places foot traffic, business listings, reviews) to score every commercial property and surface actionable opportunities.
              </p>
              <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-2 max-w-2xl">
                <div className="rounded-lg bg-white/5 border border-white/10 px-3 py-2">
                  <p className="text-[11px] text-indigo-400 font-semibold uppercase tracking-wide">Ask</p>
                  <p className="text-xs text-indigo-100 mt-0.5">Query the AI for top opportunities by role</p>
                </div>
                <div className="rounded-lg bg-white/5 border border-white/10 px-3 py-2">
                  <p className="text-[11px] text-indigo-400 font-semibold uppercase tracking-wide">Compare</p>
                  <p className="text-xs text-indigo-100 mt-0.5">Side-by-side property scores across 5 dimensions</p>
                </div>
                <div className="rounded-lg bg-white/5 border border-white/10 px-3 py-2">
                  <p className="text-[11px] text-indigo-400 font-semibold uppercase tracking-wide">Explore</p>
                  <p className="text-xs text-indigo-100 mt-0.5">Interactive map with 10 data layers</p>
                </div>
              </div>
              <div className="mt-3 flex items-center gap-4 text-xs">
                <span className="flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${apiStatus === 'ok' ? 'bg-emerald-400 animate-pulse' : apiStatus === 'down' ? 'bg-rose-400' : 'bg-amber-400 animate-pulse'}`} />
                  {apiStatus === 'ok' ? 'Connected' : apiStatus === 'down' ? 'Offline' : 'Connecting…'}
                </span>
                <span className="text-indigo-400">·</span>
                <span className="text-indigo-300">
                  {ROLE_TABS.find(t => t.id === activeRole)?.label ?? 'Residents'} View
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={onRefreshSignals}
                disabled={refreshingSignals}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 backdrop-blur border border-white/20 text-white text-sm font-medium hover:bg-white/20 disabled:opacity-50 transition-all"
              >
                {refreshingSignals ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                Refresh Signals
              </button>
              <Link
                to="/site"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-500/80 backdrop-blur border border-indigo-400/30 text-white text-sm font-medium hover:bg-indigo-500 transition-all"
              >
                <Map className="w-4 h-4" />
                Site Map
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-4 md:p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Choose your perspective</p>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {ROLE_TABS.map((tab) => {
              const isActive = tab.id === activeRole;
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveRole(tab.id)}
                  className={`min-w-fit px-4 py-3 rounded-xl border text-left transition-all ${
                    isActive
                      ? 'bg-gradient-to-br from-indigo-600 to-indigo-700 text-white border-indigo-600 shadow-md shadow-indigo-200'
                      : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4" />
                    <span className="font-semibold text-sm">{tab.label}</span>
                  </div>
                  <p className={`text-xs mt-1 ${isActive ? 'text-indigo-100' : 'text-slate-500'}`}>{tab.blurb}</p>
                </button>
              );
            })}
          </div>

          <div className="mt-4 flex items-center justify-between gap-4 flex-wrap">
            <ScenarioSelector activeScenario={activeScenario} onSelect={selectScenario} />
          </div>
        </section>

        {error && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 text-rose-700 px-4 py-3 text-sm flex items-center gap-2">
            <Activity className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {loadingOverview ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mx-auto" />
            <p className="mt-4 text-slate-500 text-sm">Analyzing opportunities for {ROLE_TABS.find(t => t.id === activeRole)?.label ?? 'you'}…</p>
          </div>
        ) : (
          <>
            <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="rounded-xl border border-slate-200 bg-white p-4 hover:shadow-md transition-shadow">
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-medium">Role Focus</p>
                <p className="mt-1.5 text-sm font-semibold text-slate-900">{overview?.role_focus ?? '—'}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-4 hover:shadow-md transition-shadow">
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-medium">Properties Analyzed</p>
                <p className="mt-1.5 text-2xl font-bold text-slate-900">{overview?.total_properties ?? 0}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-4 hover:shadow-md transition-shadow">
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-medium">Top Avg Score</p>
                <p className="mt-1.5 text-2xl font-bold text-indigo-600">{String(overview?.kpis?.avg_top_score ?? '0')}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-white p-4 hover:shadow-md transition-shadow">
                <p className="text-[11px] text-slate-500 uppercase tracking-wider font-medium">Confidence</p>
                <p className="mt-1.5 text-2xl font-bold text-emerald-600">{Math.round((overview?.confidence ?? 0) * 100)}%</p>
              </div>
            </section>

            <section className="grid grid-cols-1 xl:grid-cols-3 gap-4">
              <div className="xl:col-span-2 space-y-3">
                {displayedRecommendations.map((item) => (
                  <article key={item.property.id} className="rounded-xl border border-slate-200 bg-white p-5 hover:shadow-md transition-shadow group">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-indigo-500 bg-indigo-50 px-2 py-0.5 rounded-md">#{item.rank}</span>
                          <h3 className="text-base font-semibold text-slate-900">{item.property.address}</h3>
                        </div>
                        <p className="text-sm text-slate-500 mt-0.5">{item.property.neighborhood || 'Montgomery, AL'}</p>
                      </div>
                      <span className={`px-3 py-1.5 rounded-lg border font-bold text-sm ${scoreClass(item.scores.overall_score)}`}>
                        {item.scores.overall_score.toFixed(1)}
                      </span>
                    </div>

                    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2">
                      {[
                        { label: 'Resident Fit', value: item.scores.resident_fit_score, icon: Users },
                        { label: 'Business', value: item.scores.business_opportunity_score, icon: Briefcase },
                        { label: 'City Impact', value: item.scores.city_impact_score, icon: Building2 },
                        { label: 'Evidence', value: item.evidence_ids.length, icon: ShieldCheck },
                      ].map(({ label, value, icon: Icon }) => (
                        <div key={label} className="rounded-lg bg-slate-50 px-3 py-2.5 border border-slate-100">
                          <div className="flex items-center gap-1.5 text-slate-500 mb-1">
                            <Icon className="w-3 h-3" />
                            <span className="text-[11px] font-medium">{label}</span>
                          </div>
                          <p className="text-sm font-bold text-slate-800">{typeof value === 'number' && label !== 'Evidence' ? value.toFixed(1) : value}</p>
                        </div>
                      ))}
                    </div>

                    <div className="mt-3 flex gap-2 flex-wrap">
                      {item.top_factors.map((factor) => (
                        <span key={factor} className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100">
                          {factor}
                        </span>
                      ))}
                    </div>
                  </article>
                ))}
              </div>

              <aside className="space-y-3">
                <section className="rounded-xl border border-slate-200 bg-white p-4">
                  <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-indigo-500" />
                    Data Sources & Trust
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">Montgomery open data + Bright Data web signals with confidence scores.</p>
                  <div className="mt-3 space-y-2 max-h-60 overflow-auto">
                    {(recommendation?.sources ?? overview?.sources ?? []).slice(0, 8).map((source) => (
                      <div key={source.id} className="rounded-lg border border-slate-100 bg-slate-50 p-2.5">
                        <div className="flex items-center justify-between">
                          <p className="text-xs font-semibold text-slate-800">{source.label}</p>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${source.is_live ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                            {source.is_live ? 'Live' : 'Cached'}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 mt-0.5">{source.source_type} · {Math.round(source.confidence * 100)}% confidence</p>
                      </div>
                    ))}
                  </div>
                </section>

                <section className="rounded-xl border border-slate-200 bg-white p-4">
                  <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-indigo-500" />
                    Signal Change Feed
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">Activity changes in the last 48 hours.</p>
                  <div className="mt-3 space-y-2 max-h-60 overflow-auto">
                    {(changes?.changes ?? []).slice(0, 6).map((change) => (
                      <div key={change.property_id} className="rounded-lg border border-slate-100 bg-slate-50 p-2.5">
                        <p className="text-xs font-medium text-slate-800 truncate">{change.address}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs font-bold ${change.delta_activity_index >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                            {change.delta_activity_index >= 0 ? '+' : ''}{change.delta_activity_index.toFixed(2)}
                          </span>
                          <span className="text-[10px] text-slate-400">activity index</span>
                        </div>
                      </div>
                    ))}
                    {!changes?.changes?.length && (
                      <p className="text-xs text-slate-400 py-4 text-center">No recent changes. Click "Refresh Signals" to generate deltas.</p>
                    )}
                  </div>
                </section>

              </aside>
            </section>
          </>
        )}
      </div>
    </div>
  );
}
