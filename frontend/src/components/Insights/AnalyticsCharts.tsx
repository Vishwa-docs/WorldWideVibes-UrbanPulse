import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts';
import type { PieLabelRenderProps } from 'recharts';
import { Loader2, Building2, MapPin, Briefcase, Users, TrendingUp } from 'lucide-react';
import {
  fetchBusinessLicenses,
  fetchMostVisited,
  fetch311Requests,
  fetchProperties,
  fetchWorkforceData,
} from '../../services/api';
import type {
  BusinessLicense,
  MostVisitedLocation,
  ServiceRequest311,
  Property,
  WorkforceData,
} from '../../types';

const CHART_COLORS = [
  '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#3b82f6',
];

export default function AnalyticsCharts() {
  const [licenses, setLicenses] = useState<BusinessLicense[]>([]);
  const [visited, setVisited] = useState<MostVisitedLocation[]>([]);
  const [requests311, setRequests311] = useState<ServiceRequest311[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [workforce, setWorkforce] = useState<WorkforceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    Promise.allSettled([
      fetchBusinessLicenses(500).then(r => r.items),
      fetchMostVisited(200).then(r => r.items),
      fetch311Requests(500).then(r => r.items),
      fetchProperties({ limit: 200 }),
      fetchWorkforceData(),
    ]).then(([licRes, visRes, reqRes, propRes, wfRes]) => {
      if (cancelled) return;
      if (licRes.status === 'fulfilled') setLicenses(licRes.value);
      if (visRes.status === 'fulfilled') setVisited(visRes.value);
      if (reqRes.status === 'fulfilled') setRequests311(reqRes.value);
      if (propRes.status === 'fulfilled') setProperties(propRes.value);
      if (wfRes.status === 'fulfilled') setWorkforce(wfRes.value);
      setLoading(false);
    });

    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
        <span className="ml-3 text-sm text-gray-500">Loading Montgomery analytics…</span>
      </div>
    );
  }

  // ── Business License Distribution ─────────────────────────────
  const licenseByType: Record<string, number> = {};
  licenses.forEach(l => {
    const type = l.business_type || 'Unknown';
    licenseByType[type] = (licenseByType[type] || 0) + 1;
  });
  const licenseChartData = Object.entries(licenseByType)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([name, count]) => ({ name: name.length > 18 ? name.slice(0, 16) + '…' : name, count }));

  // ── 311 Requests by Category ──────────────────────────────────
  const requestsByCategory: Record<string, number> = {};
  requests311.forEach(r => {
    const cat = r.category || 'Unknown';
    requestsByCategory[cat] = (requestsByCategory[cat] || 0) + 1;
  });
  const requestsChartData = Object.entries(requestsByCategory)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, count]) => ({ name: name.length > 18 ? name.slice(0, 16) + '…' : name, count }));

  // ── Property Type Breakdown ───────────────────────────────
  const typeCount: Record<string, number> = {};
  properties.forEach(p => {
    const t = p.property_type || 'Unknown';
    typeCount[t] = (typeCount[t] || 0) + 1;
  });
  const propertyTypePieData = Object.entries(typeCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value }));

  // ── Score Distribution ────────────────────────────────────────
  const scoreBuckets = [
    { range: '0–20', count: 0 },
    { range: '20–40', count: 0 },
    { range: '40–60', count: 0 },
    { range: '60–80', count: 0 },
    { range: '80–100', count: 0 },
  ];
  properties.forEach(p => {
    const s = p.score?.overall_score ?? 0;
    if (s < 20) scoreBuckets[0].count++;
    else if (s < 40) scoreBuckets[1].count++;
    else if (s < 60) scoreBuckets[2].count++;
    else if (s < 80) scoreBuckets[3].count++;
    else scoreBuckets[4].count++;
  });

  // ── Foot Traffic Top Locations ────────────────────────────────
  const footTrafficData = visited
    .sort((a, b) => b.visits - a.visits)
    .slice(0, 8)
    .map(v => ({
      name: (v.name || 'Unknown').length > 16 ? (v.name || 'Unknown').slice(0, 14) + '…' : (v.name || 'Unknown'),
      visits: v.visits,
      visitors: v.visitors,
    }));

  // ── Workforce Industry Breakdown ──────────────────────────────
  const industryData = (workforce?.industries ?? [])
    .sort((a, b) => b.employed - a.employed)
    .slice(0, 8)
    .map(i => ({
      name: i.industry.length > 20 ? i.industry.slice(0, 18) + '…' : i.industry,
      employed: i.employed,
      pct: i.percentage,
    }));

  // ── Business Licenses vs Foot Traffic Radar (challenge alignment!) ──
  const licenseCategories = Object.entries(licenseByType).slice(0, 6);
  const visitedCategories: Record<string, number> = {};
  visited.forEach(v => {
    const cat = v.category || 'Other';
    visitedCategories[cat] = (visitedCategories[cat] || 0) + v.visits;
  });
  const radarCategories = licenseCategories.map(([cat, licCount]) => ({
    category: cat.length > 12 ? cat.slice(0, 10) + '…' : cat,
    licenses: licCount,
    footTraffic: Math.round((visitedCategories[cat] || 0) / 100),
  }));

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center gap-2">
        <div className="p-2 rounded-lg bg-indigo-100">
          <TrendingUp className="w-5 h-5 text-indigo-600" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-gray-900">Montgomery Data Analytics</h2>
          <p className="text-xs text-gray-500">
            Live data from Montgomery Open Data Portal + Bright Data signals · {licenses.length} business licenses · {properties.length} properties · {requests311.length} service requests
          </p>
        </div>
      </div>

      {/* Row 1: Business Licenses + Foot Traffic */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Business License Distribution */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <Briefcase className="w-4 h-4 text-indigo-600" />
            <h3 className="text-sm font-semibold text-gray-800">Business Licenses by Type</h3>
            <span className="text-xs text-gray-400 ml-auto">{licenses.length} total</span>
          </div>
          {licenseChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={licenseChartData} margin={{ top: 5, right: 10, left: -10, bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 text-center py-8">No business license data available</p>
          )}
        </div>

        {/* Foot Traffic Top Locations */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-4 h-4 text-emerald-600" />
            <h3 className="text-sm font-semibold text-gray-800">Top Foot Traffic Locations</h3>
            <span className="text-xs text-gray-400 ml-auto">{visited.length} locations</span>
          </div>
          {footTrafficData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={footTrafficData} margin={{ top: 5, right: 10, left: -10, bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
                />
                <Bar dataKey="visits" fill="#10b981" radius={[4, 4, 0, 0]} name="Visits" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 text-center py-8">No foot traffic data available</p>
          )}
        </div>
      </div>

      {/* Row 2: Property Analysis + 311 Requests */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Property Type Breakdown */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <Building2 className="w-4 h-4 text-indigo-600" />
            <h3 className="text-sm font-semibold text-gray-800">Property Types</h3>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={propertyTypePieData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
                label={(props: PieLabelRenderProps) => `${props.name ?? ''} ${(((props.percent as number) ?? 0) * 100).toFixed(0)}%`}
              >
                {propertyTypePieData.map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Property Score Distribution */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="w-4 h-4 text-indigo-600" />
            <h3 className="text-sm font-semibold text-gray-800">Score Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={scoreBuckets} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="range" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {scoreBuckets.map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 311 Service Requests */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <Building2 className="w-4 h-4 text-amber-600" />
            <h3 className="text-sm font-semibold text-gray-800">311 Requests by Type</h3>
            <span className="text-xs text-gray-400 ml-auto">{requests311.length}</span>
          </div>
          {requestsChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={requestsChartData} layout="vertical" margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10 }} width={100} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                <Bar dataKey="count" fill="#f59e0b" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 text-center py-8">No 311 data available</p>
          )}
        </div>
      </div>

      {/* Row 3: Workforce + Business vs Foot Traffic Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Workforce Industry Breakdown */}
        {industryData.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-4 h-4 text-purple-600" />
              <h3 className="text-sm font-semibold text-gray-800">Workforce: Top Industries</h3>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={industryData} layout="vertical" margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10 }} width={130} />
                <Tooltip
                  contentStyle={{ fontSize: 12, borderRadius: 8 }}
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  formatter={(value: any) =>
                    [typeof value === 'number' ? value.toLocaleString() : String(value), 'Employed']
                  }
                />
                <Bar dataKey="employed" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Business Licenses vs Foot Traffic Radar */}
        {radarCategories.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <Briefcase className="w-4 h-4 text-indigo-600" />
              <h3 className="text-sm font-semibold text-gray-800">Licenses vs. Foot Traffic</h3>
              <span className="text-[10px] text-gray-400 ml-auto">Challenge: compare business licenses with foot traffic</span>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={radarCategories} cx="50%" cy="50%" outerRadius="70%">
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="category" tick={{ fontSize: 10 }} />
                <PolarRadiusAxis tick={{ fontSize: 9 }} />
                <Radar name="Licenses" dataKey="licenses" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                <Radar name="Foot Traffic (÷100)" dataKey="footTraffic" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Workforce summary stats */}
      {workforce && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            <h3 className="text-sm font-semibold text-gray-800">Workforce Snapshot — {workforce.area}</h3>
            <span className="text-xs text-gray-400 ml-auto">Source: {workforce.source}</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
            <StatCard label="Labor Force" value={workforce.employment.in_labor_force.toLocaleString()} color="indigo" />
            <StatCard label="Employed" value={workforce.employment.employed.toLocaleString()} color="emerald" />
            <StatCard label="Unemployment" value={`${workforce.employment.unemployment_rate}%`} color="red" />
            <StatCard label="Bachelor's+" value={`${workforce.education.bachelors_or_higher_pct}%`} color="purple" />
            <StatCard label="Work from Home" value={`${workforce.commuting.work_from_home.toLocaleString()}`} color="sky" />
            <StatCard label="Public Transit" value={`${workforce.commuting.public_transit.toLocaleString()}`} color="amber" />
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  const bgMap: Record<string, string> = {
    indigo: 'bg-indigo-50',
    emerald: 'bg-emerald-50',
    red: 'bg-red-50',
    purple: 'bg-purple-50',
    sky: 'bg-sky-50',
    amber: 'bg-amber-50',
  };
  const textMap: Record<string, string> = {
    indigo: 'text-indigo-700',
    emerald: 'text-emerald-700',
    red: 'text-red-700',
    purple: 'text-purple-700',
    sky: 'text-sky-700',
    amber: 'text-amber-700',
  };
  return (
    <div className={`rounded-lg ${bgMap[color] ?? 'bg-gray-50'} p-3 text-center`}>
      <p className={`text-lg font-bold ${textMap[color] ?? 'text-gray-700'}`}>{value}</p>
      <p className="text-[10px] text-gray-500 uppercase tracking-wide mt-0.5">{label}</p>
    </div>
  );
}
