import { useState, useEffect } from 'react';
import { Footprints, Loader2 } from 'lucide-react';
import { fetchWalkScore } from '../../services/api';
import type { WalkScoreResponse } from '../../types';

interface WalkScoreGaugeProps {
  propertyId: number;
  compact?: boolean;
}

function scoreGradient(score: number): string {
  if (score >= 90) return 'from-emerald-500 to-emerald-400';
  if (score >= 70) return 'from-green-500 to-emerald-400';
  if (score >= 50) return 'from-amber-500 to-yellow-400';
  if (score >= 25) return 'from-orange-500 to-amber-400';
  return 'from-red-500 to-orange-400';
}

function scoreBg(score: number): string {
  if (score >= 90) return 'bg-emerald-50 border-emerald-200 text-emerald-700';
  if (score >= 70) return 'bg-green-50 border-green-200 text-green-700';
  if (score >= 50) return 'bg-amber-50 border-amber-200 text-amber-700';
  if (score >= 25) return 'bg-orange-50 border-orange-200 text-orange-700';
  return 'bg-red-50 border-red-200 text-red-700';
}

const CATEGORY_ICONS: Record<string, string> = {
  grocery_or_supermarket: '🛒',
  restaurant: '🍽️',
  school: '🏫',
  park: '🌳',
  pharmacy: '💊',
  transit_station: '🚌',
  bus_station: '🚏',
  hospital: '🏥',
  library: '📚',
  gym: '💪',
  cafe: '☕',
  bank: '🏦',
  shopping_mall: '🛍️',
};

export default function WalkScoreGauge({ propertyId, compact = false }: WalkScoreGaugeProps) {
  const [data, setData] = useState<WalkScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchWalkScore(propertyId)
      .then((res) => { if (!cancelled) setData(res); })
      .catch(() => { if (!cancelled) setError('Unable to load walk score'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [propertyId]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 py-2">
        <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
        <span className="text-xs text-gray-400">Loading walk score...</span>
      </div>
    );
  }

  if (error || !data) {
    return null;
  }

  if (compact) {
    return (
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-sm font-bold ${scoreBg(data.walk_score)}`}>
        <Footprints className="w-3.5 h-3.5" />
        {data.walk_score}
      </div>
    );
  }

  const arcPercent = (data.walk_score / 100) * 100;
  const topCategories = Object.entries(data.category_breakdown || {})
    .map(([key, val]) => ({ category: key, count: val.count, weighted_score: val.weighted_score }))
    .sort((a, b) => b.count - a.count)
    .filter((c) => c.count > 0)
    .slice(0, 6);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500">
          <Footprints className="w-4 h-4 text-white" />
        </div>
        <h3 className="text-sm font-semibold text-gray-800">Walk Score</h3>
      </div>

      {/* Score circle */}
      <div className="flex items-center gap-4 mb-3">
        <div className="relative w-20 h-20 flex-shrink-0">
          <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
            <circle cx="50" cy="50" r="42" fill="none" stroke="#f3f4f6" strokeWidth="8" />
            <circle
              cx="50" cy="50" r="42" fill="none"
              strokeWidth="8"
              strokeLinecap="round"
              className={`bg-gradient-to-r ${scoreGradient(data.walk_score)}`}
              stroke="currentColor"
              style={{
                strokeDasharray: `${arcPercent * 2.64} 264`,
                color: data.walk_score >= 70 ? '#10b981' : data.walk_score >= 50 ? '#f59e0b' : '#ef4444',
              }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-xl font-bold text-gray-900">{data.walk_score}</span>
            <span className="text-[9px] text-gray-400">/ 100</span>
          </div>
        </div>
        <div>
          <p className={`text-sm font-semibold ${data.walk_score >= 70 ? 'text-emerald-600' : data.walk_score >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
            {data.label}
          </p>
          <p className="text-xs text-gray-400 mt-0.5">{data.total_amenities_nearby} amenities nearby</p>
        </div>
      </div>

      {/* Category breakdown */}
      {topCategories.length > 0 && (
        <div className="grid grid-cols-3 gap-1.5">
          {topCategories.map((cat) => (
            <div key={cat.category} className="bg-gray-50 rounded-lg px-2 py-1.5 text-center">
              <span className="text-sm">{CATEGORY_ICONS[cat.category] || '📍'}</span>
              <p className="text-xs font-bold text-gray-700 mt-0.5">{cat.count}</p>
              <p className="text-[9px] text-gray-400 capitalize truncate">{cat.category.replace('_', ' ')}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
