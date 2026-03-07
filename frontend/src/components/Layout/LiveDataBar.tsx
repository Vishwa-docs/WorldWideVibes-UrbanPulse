import { useState, useEffect } from 'react';
import { Database, CheckCircle2, Loader2, Zap, Globe, FileText } from 'lucide-react';
import { fetchDataSources } from '../../services/api';
import type { DataSourcesSummary } from '../../types';

/**
 * Compact live data status bar showing connected data sources.
 * Placed on the dashboard to demonstrate real-time data integration.
 */
export default function LiveDataBar() {
  const [data, setData] = useState<DataSourcesSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDataSources()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 border-b border-gray-200">
        <Loader2 className="w-3 h-3 animate-spin text-gray-400" />
        <span className="text-[10px] text-gray-400">Connecting data sources...</span>
      </div>
    );
  }

  if (!data) return null;

  const liveCount = Object.values(data.sources).filter(s => s.available).length;

  return (
    <div className="flex items-center gap-2 px-4 py-1.5 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 overflow-x-auto">
      {/* Live indicator */}
      <div className="flex items-center gap-1.5 flex-shrink-0">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
        <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider">
          {liveCount} Live Sources
        </span>
      </div>

      <div className="w-px h-4 bg-gray-300 flex-shrink-0" />

      {/* Source badges */}
      {Object.entries(data.sources).map(([key, info]) => {
        const isBD = key === 'brightdata';
        return (
          <div
            key={key}
            className={`flex items-center gap-1 px-2 py-0.5 rounded-full flex-shrink-0 ${
              isBD
                ? 'bg-orange-100 border border-orange-200'
                : 'bg-white border border-gray-200'
            }`}
          >
            {isBD ? (
              <Zap className="w-2.5 h-2.5 text-orange-500" />
            ) : key.includes('311') ? (
              <FileText className="w-2.5 h-2.5 text-gray-500" />
            ) : (
              <Globe className="w-2.5 h-2.5 text-gray-500" />
            )}
            <span className={`text-[9px] font-medium whitespace-nowrap ${
              isBD ? 'text-orange-700' : 'text-gray-600'
            }`}>
              {key === 'brightdata' ? 'Bright Data' : 
               key === '311_requests' ? '311' :
               key === 'most_visited' ? 'Foot Traffic' :
               key === 'visitor_origin' ? 'Visitors' :
               key === 'business_licenses' ? 'Businesses' :
               key === 'workforce' ? 'Workforce' : key}
            </span>
            {info.available && (
              <CheckCircle2 className={`w-2.5 h-2.5 ${isBD ? 'text-orange-500' : 'text-emerald-500'}`} />
            )}
          </div>
        );
      })}

      {/* Montgomery Open Data label */}
      <div className="ml-auto flex items-center gap-1 flex-shrink-0">
        <Database className="w-3 h-3 text-gray-400" />
        <span className="text-[9px] text-gray-400 font-medium whitespace-nowrap">Montgomery Open Data + Census + Bright Data</span>
      </div>
    </div>
  );
}
