import { TrendingUp, Star, GitCompareArrows, Shield, Footprints, BarChart3, Heart, Activity, Loader2, Zap } from 'lucide-react';
import WalkScoreGauge from '../Insights/WalkScoreGauge';
import SiteReportButton from '../Insights/SiteReportButton';
import InvestmentAnalysisButton from '../Insights/InvestmentAnalysisButton';
import type { Property, ScorecardResponse, PersonaType } from '../../types';

interface PropertyScorecardProps {
  property: Property;
  scorecard?: ScorecardResponse | null;
  persona: PersonaType;
  onAddToCompare?: (id: number) => void;
  onToggleWatchlist?: (id: number) => void;
  isWatched?: boolean;
  loading?: boolean;
}

interface ScoreRow {
  key: string;
  label: string;
  cityLabel: string;
  entrepreneurLabel: string;
  value: number;
  icon: typeof TrendingUp;
}

function getScoreRows(scores: { foot_traffic_score: number; competition_score: number; safety_score: number; equity_score: number; activity_index: number }): ScoreRow[] {
  return [
    { key: 'foot_traffic', label: 'Foot Traffic', cityLabel: 'Pedestrian Flow', entrepreneurLabel: 'Customer Traffic', value: scores.foot_traffic_score, icon: Footprints },
    { key: 'competition', label: 'Competition', cityLabel: 'Market Saturation', entrepreneurLabel: 'Competition Gap', value: scores.competition_score, icon: BarChart3 },
    { key: 'safety', label: 'Safety', cityLabel: 'Public Safety', entrepreneurLabel: 'Safety Score', value: scores.safety_score, icon: Shield },
    { key: 'equity', label: 'Equity', cityLabel: 'Equity Index', entrepreneurLabel: 'Community Need', value: scores.equity_score, icon: Heart },
    { key: 'activity', label: 'Activity', cityLabel: 'Activity Index', entrepreneurLabel: 'Buzz Factor', value: scores.activity_index, icon: Activity },
  ];
}

function scoreColor(value: number): string {
  if (value >= 7) return 'bg-emerald-500';
  if (value >= 4) return 'bg-amber-500';
  return 'bg-red-500';
}

function overallColor(value: number): string {
  if (value >= 7) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
  if (value >= 4) return 'text-amber-600 bg-amber-50 border-amber-200';
  return 'text-red-600 bg-red-50 border-red-200';
}

export default function PropertyScorecard({
  property,
  scorecard,
  persona,
  onAddToCompare,
  onToggleWatchlist,
  isWatched = false,
  loading = false,
}: PropertyScorecardProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
          <span className="ml-2 text-sm text-gray-500">Loading scorecard...</span>
        </div>
      </div>
    );
  }

  const scores = scorecard?.scores ?? property.score;
  const overallScore = scores?.overall_score;
  const rows = scores ? getScoreRows(scores) : [];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-4 h-4 text-indigo-600 flex-shrink-0" />
            <h3 className="text-sm font-semibold text-gray-900 truncate">{property.address}</h3>
          </div>
          <p className="text-xs text-gray-500">
            {property.neighborhood || 'Montgomery, AL'}
            {property.lot_size_sqft && ` · ${property.lot_size_sqft.toLocaleString()} sqft`}
          </p>
        </div>
        {overallScore != null && (
          <div className={`px-3 py-1.5 rounded-lg border text-lg font-bold ${overallColor(overallScore)}`}>
            {overallScore.toFixed(1)}
          </div>
        )}
      </div>

      {/* Score bars */}
      {rows.length > 0 && (
        <div className="space-y-2.5 mb-3">
          {rows.map((row) => {
            const Icon = row.icon;
            const label = persona === 'city_console' ? row.cityLabel : row.entrepreneurLabel;
            return (
              <div key={row.key}>
                <div className="flex items-center justify-between text-xs mb-0.5">
                  <span className="flex items-center gap-1.5 text-gray-600 font-medium">
                    <Icon className="w-3 h-3" />
                    {label}
                  </span>
                  <span className="text-gray-500 font-medium">{row.value.toFixed(1)}/10</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all duration-500 ${scoreColor(row.value)}`}
                    style={{ width: `${(row.value / 10) * 100}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Nearby info */}
      {scorecard && (
        <div className="flex gap-3 mb-3">
          <div className="flex-1 bg-gray-50 rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-gray-800">{scorecard.nearby_services.length}</p>
            <p className="text-[10px] text-gray-500 uppercase tracking-wider">Services</p>
          </div>
          <div className="flex-1 bg-gray-50 rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-gray-800">{scorecard.nearby_incidents.length}</p>
            <p className="text-[10px] text-gray-500 uppercase tracking-wider">Incidents</p>
          </div>
        </div>
      )}

      {/* AI Narrative */}
      {scorecard?.ai_narrative && (
        <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-3 mb-3">
          <p className="text-xs text-indigo-800 leading-relaxed">{scorecard.ai_narrative}</p>
        </div>
      )}

      {/* Walk Score */}
      <div className="mb-3">
        <WalkScoreGauge propertyId={property.id} />
      </div>

      {/* AI Insights */}
      <div className="space-y-2 mb-3">
        <SiteReportButton propertyId={property.id} propertyAddress={property.address} />
        <InvestmentAnalysisButton propertyId={property.id} propertyAddress={property.address} />
      </div>

      {/* Bright Data attribution */}
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 mb-3 bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200 rounded-lg">
        <Zap className="w-3 h-3 text-orange-500 flex-shrink-0" />
        <p className="text-[10px] text-orange-700">
          Activity scores powered by <span className="font-semibold">Bright Data</span> web signals
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        {onAddToCompare && (
          <button
            onClick={() => onAddToCompare(property.id)}
            className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors"
          >
            <GitCompareArrows className="w-3.5 h-3.5" />
            Compare
          </button>
        )}
        {onToggleWatchlist && (
          <button
            onClick={() => onToggleWatchlist(property.id)}
            className={`flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${
              isWatched
                ? 'text-amber-600 bg-amber-50 border-amber-200 hover:bg-amber-100'
                : 'text-gray-500 bg-white border-gray-200 hover:bg-gray-50'
            }`}
          >
            <Star className={`w-3.5 h-3.5 ${isWatched ? 'fill-amber-400' : ''}`} />
            {isWatched ? 'Starred' : 'Star'}
          </button>
        )}
      </div>
    </div>
  );
}
