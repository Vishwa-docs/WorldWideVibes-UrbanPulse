import { useState } from 'react';
import { TrendingUp, Loader2 } from 'lucide-react';
import { fetchInvestmentAnalysis } from '../../services/api';
import type { InvestmentAnalysisResponse } from '../../types';

interface InvestmentAnalysisButtonProps {
  propertyId: number;
  propertyAddress: string;
}

export default function InvestmentAnalysisButton({ propertyId, propertyAddress }: InvestmentAnalysisButtonProps) {
  const [analysis, setAnalysis] = useState<InvestmentAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  const handleGenerate = async () => {
    if (analysis) {
      setExpanded(!expanded);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchInvestmentAnalysis(propertyId);
      setAnalysis(data);
      setExpanded(true);
    } catch {
      setError('Failed to generate investment analysis');
    } finally {
      setLoading(false);
    }
  };

  const sections = analysis?.analysis
    ? analysis.analysis.split(/(?=^#{1,3}\s)/m).filter(Boolean)
    : [];

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500">
            <TrendingUp className="w-4 h-4 text-white" />
          </div>
          <div className="text-left">
            <p className="text-sm font-semibold text-gray-800">Investment Analysis</p>
            <p className="text-[10px] text-gray-400">{analysis ? 'Click to toggle' : 'AI-powered ROI assessment'}</p>
          </div>
        </div>
        {loading && <Loader2 className="w-4 h-4 animate-spin text-emerald-500" />}
      </button>

      {error && (
        <div className="px-4 pb-3">
          <p className="text-xs text-red-500">{error}</p>
        </div>
      )}

      {expanded && analysis && (
        <div className="border-t border-gray-100 px-4 py-3 max-h-96 overflow-y-auto">
          <p className="text-xs text-gray-400 mb-2">
            {propertyAddress} &middot; {new Date(analysis.generated_at).toLocaleDateString()}
          </p>
          {sections.length > 0 ? (
            <div className="space-y-3">
              {sections.map((section, i) => {
                const lines = section.trim().split('\n');
                const heading = lines[0]?.replace(/^#+\s*/, '').trim();
                const body = lines.slice(1).join('\n').trim();
                return (
                  <div key={i}>
                    {heading && (
                      <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wider mb-1">{heading}</p>
                    )}
                    {body && (
                      <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-wrap">{body}</p>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-wrap">{analysis.analysis}</p>
          )}
        </div>
      )}
    </div>
  );
}
