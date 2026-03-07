import { useState, useEffect } from 'react';
import { Loader2, BarChart3, MapPin, Sparkles, TrendingUp } from 'lucide-react';
import { useScenario } from '../hooks/useScenario';
import ScenarioSelector from '../components/Scenario/ScenarioSelector';
import DemographicsPanel from '../components/Insights/DemographicsPanel';
import WorkforcePanel from '../components/Insights/WorkforcePanel';
import DataSourcesPanel from '../components/Insights/DataSourcesPanel';
import { fetchMarketGaps, fetchProperties } from '../services/api';
import type { MarketGapResponse, Property } from '../types';

export default function Insights() {
  const { activeScenario, selectScenario } = useScenario();
  const [marketGaps, setMarketGaps] = useState<MarketGapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [properties, setProperties] = useState<Property[]>([]);

  useEffect(() => {
    fetchProperties({ limit: 200 }).then(setProperties).catch(() => {});
  }, []);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMarketGaps(activeScenario);
      setMarketGaps(data);
    } catch {
      setError('Failed to generate market analysis');
    } finally {
      setLoading(false);
    }
  };

  // Parse sections from analysis text
  const analysisSections = marketGaps?.analysis
    ? marketGaps.analysis.split(/(?=^#{1,3}\s)/m).filter(Boolean)
    : [];

  // Sort service distribution
  const serviceEntries = Object.entries(marketGaps?.service_distribution || {})
    .sort((a, b) => b[1] - a[1]);

  const barColors = [
    'bg-indigo-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500',
    'bg-sky-500', 'bg-purple-500', 'bg-orange-500', 'bg-teal-500',
    'bg-pink-500', 'bg-cyan-500',
  ];

  const maxService = serviceEntries.length > 0 ? serviceEntries[0][1] : 1;

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Challenge Statement Banner */}
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 rounded-xl p-5 mb-6 shadow-lg">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-white/15 rounded-lg flex-shrink-0">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-[10px] font-bold text-indigo-200 uppercase tracking-widest mb-1">
                World Wide Vibes Hackathon · Challenge Track
              </p>
              <h2 className="text-lg font-bold text-white leading-tight mb-2">
                Workforce, Business &amp; Economic Growth
              </h2>
              <p className="text-sm text-indigo-200 leading-relaxed">
                How can <span className="font-semibold text-white">Montgomery, AL</span> attract new businesses,
                support existing ones, and revitalize underserved areas through data-driven insights?
                UrbanPulse answers this by combining{' '}
                <span className="font-semibold text-white">real-time web signals</span>,{' '}
                <span className="font-semibold text-white">open city data</span>, and{' '}
                <span className="font-semibold text-white">AI analysis</span>{' '}
                to identify optimal locations for economic development.
              </p>
            </div>
          </div>
        </div>

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">City Insights</h1>
              <p className="text-sm text-gray-500">AI-powered market analysis & demographics for Montgomery, AL</p>
            </div>
          </div>
        </div>

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column: Demographics */}
          <div className="lg:col-span-1 space-y-4">
            <DemographicsPanel />
            <WorkforcePanel />
            <DataSourcesPanel />

            {/* Quick stats */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
              <div className="flex items-center gap-2 mb-3">
                <MapPin className="w-4 h-4 text-indigo-600" />
                <h3 className="text-sm font-semibold text-gray-800">Property Overview</h3>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-gray-900">{properties.length}</p>
                  <p className="text-[10px] text-gray-400 uppercase">Total Properties</p>
                </div>
                <div className="bg-red-50 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-red-600">{properties.filter(p => p.is_vacant).length}</p>
                  <p className="text-[10px] text-red-400 uppercase">Vacant</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-blue-600">{properties.filter(p => p.is_city_owned).length}</p>
                  <p className="text-[10px] text-blue-400 uppercase">City-Owned</p>
                </div>
                <div className="bg-emerald-50 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-emerald-600">
                    {properties.length > 0
                      ? (properties.reduce((s, p) => s + (p.score?.overall_score || 0), 0) / properties.length).toFixed(1)
                      : '—'}
                  </p>
                  <p className="text-[10px] text-emerald-400 uppercase">Avg Score</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right column: Market Gap Analysis */}
          <div className="lg:col-span-2 space-y-4">
            {/* Controls */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Select Scenario</p>
                  <ScenarioSelector activeScenario={activeScenario} onSelect={selectScenario} />
                </div>
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg text-sm font-medium hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <BarChart3 className="w-4 h-4" />
                  )}
                  Analyze Market Gaps
                </button>
              </div>
            </div>

            {/* Loading */}
            {loading && (
              <div className="flex flex-col items-center justify-center py-16">
                <Loader2 className="w-10 h-10 animate-spin text-indigo-600 mb-4" />
                <p className="text-gray-500 text-sm">Analyzing Montgomery market data...</p>
                <p className="text-gray-400 text-xs mt-1">This uses AI to identify gaps and opportunities</p>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
                {error}
              </div>
            )}

            {/* Results */}
            {marketGaps && !loading && (
              <div className="space-y-4">
                {/* Service distribution chart */}
                {serviceEntries.length > 0 && (
                  <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                    <div className="flex items-center gap-2 mb-4">
                      <TrendingUp className="w-4 h-4 text-indigo-600" />
                      <h3 className="text-sm font-semibold text-gray-800">Service Distribution</h3>
                      <span className="text-xs text-gray-400 ml-auto">{marketGaps.total_properties} properties analyzed</span>
                    </div>
                    <div className="space-y-2">
                      {serviceEntries.map(([key, value], i) => (
                        <div key={key} className="flex items-center gap-3">
                          <span className="text-xs text-gray-500 w-24 truncate capitalize">{key.replace(/_/g, ' ')}</span>
                          <div className="flex-1 bg-gray-100 rounded-full h-3">
                            <div
                              className={`h-3 rounded-full ${barColors[i % barColors.length]} transition-all duration-500`}
                              style={{ width: `${(value / maxService) * 100}%` }}
                            />
                          </div>
                          <span className="text-xs font-bold text-gray-700 w-8 text-right">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Analysis */}
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-4 h-4 text-purple-600" />
                    <h3 className="text-sm font-semibold text-gray-800">AI Market Analysis</h3>
                    <span className="text-xs text-gray-400 ml-auto">
                      {new Date(marketGaps.generated_at).toLocaleDateString()}
                    </span>
                  </div>
                  {analysisSections.length > 0 ? (
                    <div className="space-y-4">
                      {analysisSections.map((section, i) => {
                        const lines = section.trim().split('\n');
                        const heading = lines[0]?.replace(/^#+\s*/, '').trim();
                        const body = lines.slice(1).join('\n').trim();
                        return (
                          <div key={i} className="border-l-2 border-indigo-200 pl-4">
                            {heading && (
                              <p className="text-sm font-semibold text-gray-800 mb-1">{heading}</p>
                            )}
                            {body && (
                              <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">{body}</p>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">{marketGaps.analysis}</p>
                  )}
                </div>
              </div>
            )}

            {/* Default state */}
            {!marketGaps && !loading && !error && (
              <div className="text-center py-16">
                <div className="mx-auto w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mb-6">
                  <BarChart3 className="w-8 h-8 text-purple-600" />
                </div>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Market Gap Analysis</h2>
                <p className="text-gray-500 text-sm max-w-md mx-auto leading-relaxed">
                  Select a scenario and click "Analyze Market Gaps" to discover underserved areas and business opportunities in Montgomery.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
