import { useState } from 'react';
import { BookOpen, Loader2, MapPin, Sparkles } from 'lucide-react';
import { usePersona } from '../hooks/usePersona';
import { useScenario } from '../hooks/useScenario';
import ScenarioSelector from '../components/Scenario/ScenarioSelector';
import { fetchStory } from '../services/api';
import type { StoryResponse, Property } from '../types';

export default function StoryMode() {
  const { activePersona } = usePersona();
  const { activeScenario, selectScenario } = useScenario();
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setStory(null);
    try {
      const data = await fetchStory(activeScenario, activePersona);
      setStory(data);
    } catch {
      setError('Failed to generate story. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-100">
              <BookOpen className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Story Mode</h1>
              <p className="text-sm text-gray-500">AI-generated city tour based on your scenario</p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Select Scenario</p>
              <ScenarioSelector activeScenario={activeScenario} onSelect={selectScenario} />
            </div>
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              Generate City Tour
            </button>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-indigo-600 mb-4" />
            <p className="text-gray-500 text-sm">Generating your city narrative...</p>
            <p className="text-gray-400 text-xs mt-1">This may take a moment</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm mb-6">
            {error}
          </div>
        )}

        {/* Story */}
        {story && !loading && (
          <div className="space-y-6">
            {/* Title */}
            <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 rounded-xl p-6 text-white shadow-lg">
              <h2 className="text-2xl font-bold mb-2">{story.title}</h2>
              <p className="text-indigo-200 text-sm">
                {activeScenario.charAt(0).toUpperCase() + activeScenario.slice(1)} scenario ·{' '}
                {activePersona === 'city_console' ? 'City Console' : 'Entrepreneur'} view
              </p>
            </div>

            {/* Narrative */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                {story.narrative}
              </div>
            </div>

            {/* Featured Properties */}
            {story.properties && story.properties.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-indigo-600" />
                  Featured Properties
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {story.properties.map((p) => {
                    const isSelected = selectedProperty?.id === p.id;
                    return (
                      <button
                        key={p.id}
                        onClick={() => setSelectedProperty(isSelected ? null : p)}
                        className={`text-left rounded-xl border p-4 transition-all ${
                          isSelected
                            ? 'border-indigo-400 bg-indigo-50 shadow-sm'
                            : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="text-sm font-semibold text-gray-900">{p.address}</p>
                            <p className="text-xs text-gray-500 mt-0.5">
                              {p.neighborhood || 'Montgomery'} · {p.property_type.replace('_', ' ')}
                            </p>
                          </div>
                          {p.score && (
                            <span className={`px-2 py-1 rounded-lg text-sm font-bold border ${
                              p.score.overall_score >= 7
                                ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                                : p.score.overall_score >= 4
                                  ? 'text-amber-700 bg-amber-50 border-amber-200'
                                  : 'text-red-700 bg-red-50 border-red-200'
                            }`}>
                              {p.score.overall_score.toFixed(1)}
                            </span>
                          )}
                        </div>
                        <div className="flex gap-1.5 mt-2">
                          {p.is_vacant && (
                            <span className="text-[10px] font-medium bg-red-100 text-red-700 px-1.5 py-0.5 rounded">
                              Vacant
                            </span>
                          )}
                          {p.is_city_owned && (
                            <span className="text-[10px] font-medium bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                              City-Owned
                            </span>
                          )}
                        </div>

                        {/* Expanded details */}
                        {isSelected && p.score && (
                          <div className="mt-3 pt-3 border-t border-indigo-100 space-y-1.5">
                            {[
                              { label: 'Foot Traffic', value: p.score.foot_traffic_score },
                              { label: 'Competition', value: p.score.competition_score },
                              { label: 'Safety', value: p.score.safety_score },
                              { label: 'Equity', value: p.score.equity_score },
                              { label: 'Activity', value: p.score.activity_index },
                            ].map((s) => (
                              <div key={s.label} className="flex items-center gap-2">
                                <span className="text-xs text-gray-500 w-20">{s.label}</span>
                                <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                                  <div
                                    className={`h-1.5 rounded-full ${
                                      s.value >= 7 ? 'bg-emerald-500' : s.value >= 4 ? 'bg-amber-500' : 'bg-red-500'
                                    }`}
                                    style={{ width: `${(s.value / 10) * 100}%` }}
                                  />
                                </div>
                                <span className="text-xs font-medium text-gray-600 w-6 text-right">{s.value.toFixed(1)}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Default state */}
        {!story && !loading && !error && (
          <div className="text-center py-20">
            <div className="mx-auto w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mb-6">
              <Sparkles className="w-8 h-8 text-indigo-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Ready to explore Montgomery?</h2>
            <p className="text-gray-500 text-sm max-w-md mx-auto leading-relaxed">
              Select a scenario above and click "Generate City Tour" to create an AI-powered narrative about the best opportunities in the city.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
