import { useState, useEffect } from 'react';
import { Briefcase, Loader2, GraduationCap, Car, TrendingUp } from 'lucide-react';
import { fetchWorkforceData } from '../../services/api';
import type { WorkforceData } from '../../types';

function fmt(n: number | undefined): string {
  if (n == null) return 'N/A';
  return n.toLocaleString();
}

function pct(n: number | undefined): string {
  if (n == null) return 'N/A';
  return n.toFixed(1) + '%';
}

const INDUSTRY_COLORS = [
  'bg-indigo-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500',
  'bg-sky-500', 'bg-purple-500', 'bg-orange-500', 'bg-teal-500',
  'bg-pink-500', 'bg-cyan-500', 'bg-lime-500', 'bg-fuchsia-500',
  'bg-yellow-500',
];

export default function WorkforcePanel() {
  const [data, setData] = useState<WorkforceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkforceData()
      .then(setData)
      .catch(() => setError('Workforce data unavailable'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-center py-8">
        <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
        <span className="ml-2 text-sm text-gray-400">Loading workforce data...</span>
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

  const emp = data.employment;
  const edu = data.education;
  const comm = data.commuting;
  const maxIndustry = data.industries.length > 0 ? data.industries[0].employed : 1;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-3">
        <div className="flex items-center gap-2 text-white">
          <Briefcase className="w-4 h-4" />
          <h3 className="text-sm font-semibold">Workforce & Employment</h3>
        </div>
        <p className="text-emerald-200 text-xs mt-0.5">{data.area} · US Census ACS</p>
      </div>

      <div className="p-4 space-y-4">
        {/* Employment Stats */}
        {emp && (
          <>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
                  <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Employed</span>
                </div>
                <p className="text-lg font-bold text-gray-900">{fmt(emp.employed)}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <Briefcase className="w-3.5 h-3.5 text-amber-500" />
                  <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Labor Force</span>
                </div>
                <p className="text-lg font-bold text-gray-900">{fmt(emp.in_labor_force)}</p>
              </div>
            </div>

            {/* Key rates */}
            <div className="space-y-2">
              <div>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-500 font-medium">Unemployment Rate</span>
                  <span className={`font-bold ${emp.unemployment_rate > 8 ? 'text-red-600' : emp.unemployment_rate > 5 ? 'text-amber-600' : 'text-emerald-600'}`}>
                    {pct(emp.unemployment_rate)}
                  </span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${emp.unemployment_rate > 8 ? 'bg-red-500' : emp.unemployment_rate > 5 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                    style={{ width: `${Math.min(emp.unemployment_rate, 30) / 30 * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-500 font-medium">Labor Force Participation</span>
                  <span className="font-bold text-gray-700">{pct(emp.labor_force_participation_rate)}</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-indigo-500"
                    style={{ width: `${Math.min(emp.labor_force_participation_rate, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </>
        )}

        {/* Industry Breakdown */}
        {data.industries.length > 0 && (
          <div>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold mb-2">Top Industries</p>
            <div className="space-y-1.5">
              {data.industries.slice(0, 8).map((ind, i) => (
                <div key={ind.industry}>
                  <div className="flex items-center justify-between text-xs mb-0.5">
                    <span className="text-gray-500 truncate max-w-[140px]">{ind.industry}</span>
                    <span className="font-medium text-gray-600 ml-2">{pct(ind.percentage)}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full ${INDUSTRY_COLORS[i % INDUSTRY_COLORS.length]}`}
                      style={{ width: `${(ind.employed / maxIndustry) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Education */}
        {edu && (
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <GraduationCap className="w-3.5 h-3.5 text-purple-500" />
              <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Education Attainment</p>
            </div>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div className="bg-purple-50 rounded-lg py-2">
                <p className="text-sm font-bold text-purple-700">{pct(edu.bachelors_or_higher_pct)}</p>
                <p className="text-[9px] text-purple-400">Bachelor's+</p>
              </div>
              <div className="bg-indigo-50 rounded-lg py-2">
                <p className="text-sm font-bold text-indigo-700">{pct(edu.hs_or_higher_pct)}</p>
                <p className="text-[9px] text-indigo-400">HS Diploma+</p>
              </div>
            </div>
          </div>
        )}

        {/* Commuting */}
        {comm && (
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Car className="w-3.5 h-3.5 text-sky-500" />
              <p className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">Commuting</p>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-sky-50 rounded-lg py-2">
                <p className="text-sm font-bold text-sky-700">{pct(comm.drove_alone_pct)}</p>
                <p className="text-[9px] text-sky-400">Drive Alone</p>
              </div>
              <div className="bg-emerald-50 rounded-lg py-2">
                <p className="text-sm font-bold text-emerald-700">{fmt(comm.public_transit)}</p>
                <p className="text-[9px] text-emerald-400">Transit</p>
              </div>
              <div className="bg-violet-50 rounded-lg py-2">
                <p className="text-sm font-bold text-violet-700">{fmt(comm.work_from_home)}</p>
                <p className="text-[9px] text-violet-400">Remote</p>
              </div>
            </div>
          </div>
        )}

        {/* Source badge */}
        <div className="pt-2 border-t border-gray-100">
          <p className="text-[9px] text-gray-400 text-center">
            Source: US Census Bureau · ACS 5-Year Estimates
          </p>
        </div>
      </div>
    </div>
  );
}
