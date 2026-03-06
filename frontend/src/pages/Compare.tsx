import { useState, useEffect } from 'react';
import { GitCompareArrows, Loader2, X, Search } from 'lucide-react';
import { usePersona } from '../hooks/usePersona';
import { useScenario } from '../hooks/useScenario';
import ScenarioSelector from '../components/Scenario/ScenarioSelector';
import { fetchProperties, compareProperties } from '../services/api';
import type { Property, CompareResponse, ComparePropertyItem } from '../types';

function scoreColor(value: number): string {
  if (value >= 7) return 'bg-emerald-500';
  if (value >= 4) return 'bg-amber-500';
  return 'bg-red-500';
}

function overallBg(value: number): string {
  if (value >= 7) return 'text-emerald-700 bg-emerald-50 border-emerald-200';
  if (value >= 4) return 'text-amber-700 bg-amber-50 border-amber-200';
  return 'text-red-700 bg-red-50 border-red-200';
}

const SCORE_KEYS = [
  { key: 'foot_traffic_score', label: 'Foot Traffic' },
  { key: 'competition_score', label: 'Competition' },
  { key: 'safety_score', label: 'Safety' },
  { key: 'equity_score', label: 'Equity' },
  { key: 'activity_index', label: 'Activity' },
] as const;

export default function Compare() {
  const { activePersona } = usePersona();
  const { activeScenario, selectScenario } = useScenario();
  const [allProperties, setAllProperties] = useState<Property[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [comparison, setComparison] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [propsLoading, setPropsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    setPropsLoading(true);
    fetchProperties({ limit: 200 })
      .then(setAllProperties)
      .catch(() => {})
      .finally(() => setPropsLoading(false));
  }, []);

  useEffect(() => {
    if (selectedIds.length < 2) {
      setComparison(null);
      return;
    }
    setLoading(true);
    compareProperties(selectedIds, activeScenario, activePersona)
      .then(setComparison)
      .catch(() => setComparison(null))
      .finally(() => setLoading(false));
  }, [selectedIds, activeScenario, activePersona]);

  const toggleProperty = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 3 ? [...prev, id] : prev,
    );
  };

  const filteredProperties = allProperties.filter(
    (p) => p.address.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <div className="max-w-6xl mx-auto px-6 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-100">
              <GitCompareArrows className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Compare Properties</h1>
              <p className="text-sm text-gray-500">Select up to 3 properties to compare side by side</p>
            </div>
          </div>
          <ScenarioSelector activeScenario={activeScenario} onSelect={selectScenario} />
        </div>

        {/* Property selector */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 mb-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search properties by address..."
                className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Selected chips */}
          {selectedIds.length > 0 && (
            <div className="flex gap-2 mb-3 flex-wrap">
              {selectedIds.map((id) => {
                const p = allProperties.find((x) => x.id === id);
                return (
                  <span
                    key={id}
                    className="flex items-center gap-1.5 bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-full text-xs font-medium border border-indigo-200"
                  >
                    {p?.address || `#${id}`}
                    <button onClick={() => toggleProperty(id)} className="hover:text-indigo-900">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                );
              })}
            </div>
          )}

          {/* Property grid */}
          {propsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-5 h-5 animate-spin text-indigo-600" />
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-48 overflow-y-auto">
              {filteredProperties.slice(0, 40).map((p) => {
                const isSelected = selectedIds.includes(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => toggleProperty(p.id)}
                    disabled={!isSelected && selectedIds.length >= 3}
                    className={`text-left p-2 rounded-lg border text-xs transition-all ${
                      isSelected
                        ? 'border-indigo-400 bg-indigo-50'
                        : selectedIds.length >= 3
                          ? 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
                          : 'border-gray-100 bg-white hover:border-gray-200'
                    }`}
                  >
                    <p className="font-medium text-gray-800 truncate">{p.address}</p>
                    <p className="text-gray-400 truncate">{p.property_type.replace('_', ' ')}</p>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Comparison results */}
        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
            <span className="ml-3 text-gray-500">Comparing properties...</span>
          </div>
        )}

        {comparison && !loading && (
          <div>
            {/* Side by side cards */}
            <div className={`grid gap-4 mb-6 ${comparison.items.length === 2 ? 'grid-cols-2' : 'grid-cols-3'}`}>
              {comparison.items.map((item: ComparePropertyItem) => (
                <div key={item.property.id} className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                  <h3 className="text-sm font-semibold text-gray-900 mb-1 truncate">{item.property.address}</h3>
                  <p className="text-xs text-gray-500 mb-3">
                    {item.property.neighborhood || 'Montgomery'}
                    {' · '}
                    {item.property.property_type.replace('_', ' ')}
                  </p>

                  {/* Overall score */}
                  <div className={`text-center py-3 rounded-lg border mb-4 ${overallBg(item.scores.overall_score)}`}>
                    <p className="text-3xl font-bold">{item.scores.overall_score.toFixed(1)}</p>
                    <p className="text-xs mt-0.5 opacity-75">Overall Score</p>
                  </div>

                  {/* Individual scores */}
                  <div className="space-y-2.5">
                    {SCORE_KEYS.map(({ key, label }) => {
                      const value = item.scores[key];
                      return (
                        <div key={key}>
                          <div className="flex justify-between text-xs mb-0.5">
                            <span className="text-gray-600">{label}</span>
                            <span className="font-medium text-gray-800">{value.toFixed(1)}</span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-1.5">
                            <div
                              className={`h-1.5 rounded-full ${scoreColor(value)}`}
                              style={{ width: `${(value / 10) * 100}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Property details */}
                  <div className="mt-4 pt-3 border-t border-gray-100 grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <p className="text-gray-400">Lot Size</p>
                      <p className="font-medium text-gray-700">
                        {item.property.lot_size_sqft ? `${item.property.lot_size_sqft.toLocaleString()} sqft` : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400">Assessed Value</p>
                      <p className="font-medium text-gray-700">
                        {item.property.assessed_value ? `$${item.property.assessed_value.toLocaleString()}` : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400">Vacant</p>
                      <p className="font-medium text-gray-700">{item.property.is_vacant ? 'Yes' : 'No'}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">City-Owned</p>
                      <p className="font-medium text-gray-700">{item.property.is_city_owned ? 'Yes' : 'No'}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Visual bar chart comparison */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Score Comparison</h3>
              <div className="space-y-4">
                {SCORE_KEYS.map(({ key, label }) => (
                  <div key={key}>
                    <p className="text-xs text-gray-500 mb-1.5">{label}</p>
                    <div className="space-y-1">
                      {comparison.items.map((item: ComparePropertyItem, idx: number) => {
                        const value = item.scores[key];
                        const colors = ['bg-indigo-500', 'bg-emerald-500', 'bg-amber-500'];
                        return (
                          <div key={item.property.id} className="flex items-center gap-3">
                            <span className="text-[10px] text-gray-400 w-24 truncate">{item.property.address.split(',')[0]}</span>
                            <div className="flex-1 bg-gray-100 rounded-full h-2.5">
                              <div
                                className={`h-2.5 rounded-full ${colors[idx]}`}
                                style={{ width: `${(value / 10) * 100}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium text-gray-700 w-8 text-right">{value.toFixed(1)}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!comparison && !loading && selectedIds.length < 2 && (
          <div className="text-center py-16">
            <GitCompareArrows className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-400 text-sm">Select at least 2 properties above to compare</p>
          </div>
        )}
      </div>
    </div>
  );
}
