import { useState, useEffect } from 'react';
import { Users, Loader2, Home, DollarSign, Briefcase } from 'lucide-react';
import { fetchCityDemographics, fetchTractDemographics } from '../../services/api';
import type { DemographicsResponse } from '../../types';

interface DemographicsPanelProps {
  /** If provided, shows tract-level data for these coords instead of city-wide */
  lat?: number;
  lng?: number;
}

function formatNum(n: number | undefined): string {
  if (n == null) return 'N/A';
  return n.toLocaleString();
}

function formatCurrency(n: number | undefined): string {
  if (n == null) return 'N/A';
  return '$' + n.toLocaleString();
}

function formatPct(n: number | undefined): string {
  if (n == null) return 'N/A';
  return n.toFixed(1) + '%';
}

export default function DemographicsPanel({ lat, lng }: DemographicsPanelProps) {
  const [data, setData] = useState<DemographicsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    const promise = lat != null && lng != null
      ? fetchTractDemographics(lat, lng)
      : fetchCityDemographics();

    promise
      .then((res) => { if (!cancelled) setData(res); })
      .catch(() => { if (!cancelled) setError('Demographics unavailable'); })
      .finally(() => { if (!cancelled) setLoading(false); });

    return () => { cancelled = true; };
  }, [lat, lng]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-center py-8">
        <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
        <span className="ml-2 text-sm text-gray-400">Loading demographics...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <p className="text-sm text-gray-400 text-center">{error || 'No data'}</p>
      </div>
    );
  }

  const title = data.place_name || (data.tract ? `Census Tract ${data.tract}` : 'Montgomery, AL');
  const povertyRate = data.economics?.poverty_rate_pct;
  const unemploymentRate = data.economics?.unemployment_rate_pct;

  // Build race distribution bars (only _pct entries)
  const raceEntries = Object.entries(data.race || {})
    .filter(([key]) => key.endsWith('_pct'))
    .map(([key, value]) => [key.replace('_pct', '').replace(/_/g, ' '), value] as [string, number])
    .sort((a, b) => b[1] - a[1]);

  const raceColors = [
    'bg-indigo-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500',
    'bg-sky-500', 'bg-purple-500', 'bg-orange-500', 'bg-teal-500',
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3">
        <div className="flex items-center gap-2 text-white">
          <Users className="w-4 h-4" />
          <h3 className="text-sm font-semibold">Demographics</h3>
        </div>
        <p className="text-indigo-200 text-xs mt-0.5">{title}</p>
      </div>

      <div className="p-4 space-y-4">
        {/* Key metrics */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <Users className="w-3.5 h-3.5 text-indigo-500" />
              <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Population</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{formatNum(data.total_population)}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <DollarSign className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Median Income</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{formatCurrency(data.median_household_income)}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <Home className="w-3.5 h-3.5 text-blue-500" />
              <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Home Value</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{formatCurrency(data.median_home_value)}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <Briefcase className="w-3.5 h-3.5 text-amber-500" />
              <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Unemployment</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{formatPct(unemploymentRate)}</p>
          </div>
        </div>

        {/* Poverty rate bar */}
        {povertyRate != null && (
          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-gray-500 font-medium">Poverty Rate</span>
              <span className="font-bold text-gray-700">{formatPct(povertyRate)}</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${povertyRate > 20 ? 'bg-red-500' : povertyRate > 10 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                style={{ width: `${Math.min(povertyRate, 100)}%` }}
              />
            </div>
          </div>
        )}

        {/* Housing */}
        {data.housing && (
          <div>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold mb-2">Housing</p>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-blue-50 rounded-lg py-2">
                <p className="text-sm font-bold text-blue-700">{formatNum(data.housing.total_units)}</p>
                <p className="text-[9px] text-blue-400">Total Units</p>
              </div>
              <div className="bg-emerald-50 rounded-lg py-2">
                <p className="text-sm font-bold text-emerald-700">{formatNum(data.housing.owner_occupied)}</p>
                <p className="text-[9px] text-emerald-400">Owner</p>
              </div>
              <div className="bg-amber-50 rounded-lg py-2">
                <p className="text-sm font-bold text-amber-700">{formatNum(data.housing.renter_occupied)}</p>
                <p className="text-[9px] text-amber-400">Renter</p>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs mt-2">
              <span className="text-gray-400">Vacancy Rate</span>
              <span className="font-medium text-gray-600">{formatPct(data.housing.vacancy_rate_pct)}</span>
            </div>
          </div>
        )}

        {/* Race distribution */}
        {raceEntries.length > 0 && (
          <div>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold mb-2">Population Distribution</p>
            <div className="space-y-1.5">
              {raceEntries.map(([label, value], i) => (
                <div key={label}>
                  <div className="flex items-center justify-between text-xs mb-0.5">
                    <span className="text-gray-500 capitalize">{label}</span>
                    <span className="font-medium text-gray-600">{formatPct(value)}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full ${raceColors[i % raceColors.length]}`}
                      style={{ width: `${Math.min(value, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
