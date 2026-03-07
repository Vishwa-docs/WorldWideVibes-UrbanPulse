import { useState } from 'react';
import { FileText, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { fetchSiteReport } from '../../services/api';
import type { SiteReportResponse } from '../../types';

interface SiteReportButtonProps {
  propertyId: number;
  propertyAddress: string;
}

export default function SiteReportButton({ propertyId, propertyAddress }: SiteReportButtonProps) {
  const [report, setReport] = useState<SiteReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  const handleGenerate = async () => {
    if (report) {
      setExpanded(!expanded);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSiteReport(propertyId);
      setReport(data);
      setExpanded(true);
    } catch {
      setError('Failed to generate site report');
    } finally {
      setLoading(false);
    }
  };

  // Split report into sections by markdown headers
  const sections = report?.report
    ? report.report.split(/(?=^#{1,3}\s)/m).filter(Boolean)
    : [];

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-500">
            <FileText className="w-4 h-4 text-white" />
          </div>
          <div className="text-left">
            <p className="text-sm font-semibold text-gray-800">AI Site Report</p>
            <p className="text-[10px] text-gray-400">{report ? 'Click to toggle' : 'Generate comprehensive analysis'}</p>
          </div>
        </div>
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
        ) : expanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {error && (
        <div className="px-4 pb-3">
          <p className="text-xs text-red-500">{error}</p>
        </div>
      )}

      {expanded && report && (
        <div className="border-t border-gray-100 px-4 py-3 max-h-96 overflow-y-auto">
          <div className="mb-2">
            <p className="text-xs text-gray-400">
              {propertyAddress} &middot; Generated {new Date(report.generated_at).toLocaleDateString()}
            </p>
          </div>
          {sections.length > 0 ? (
            <div className="space-y-3">
              {sections.map((section, i) => {
                const lines = section.trim().split('\n');
                const heading = lines[0]?.replace(/^#+\s*/, '').trim();
                const body = lines.slice(1).join('\n').trim();
                return (
                  <div key={i}>
                    {heading && (
                      <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wider mb-1">
                        {heading}
                      </p>
                    )}
                    {body && (
                      <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-wrap">{body}</p>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-wrap">{report.report}</p>
          )}
        </div>
      )}
    </div>
  );
}
