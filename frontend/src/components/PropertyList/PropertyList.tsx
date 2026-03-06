import { Star, MapPin, Building2 } from 'lucide-react';
import type { Property, RankedPropertyItem } from '../../types';

interface PropertyListProps {
  properties: Property[];
  ranked?: RankedPropertyItem[];
  selectedId?: number;
  onSelect: (property: Property) => void;
  watchedIds?: number[];
  onToggleWatchlist?: (propertyId: number) => void;
  loading?: boolean;
}

function scoreColor(score: number): string {
  if (score >= 7) return 'text-emerald-600';
  if (score >= 4) return 'text-amber-600';
  return 'text-red-600';
}

function scoreBg(score: number): string {
  if (score >= 7) return 'bg-emerald-50 border-emerald-200';
  if (score >= 4) return 'bg-amber-50 border-amber-200';
  return 'bg-red-50 border-red-200';
}

function typeBadge(type: string): string {
  switch (type) {
    case 'vacant': return 'bg-red-100 text-red-700';
    case 'city_owned': return 'bg-blue-100 text-blue-700';
    case 'commercial': return 'bg-green-100 text-green-700';
    default: return 'bg-gray-100 text-gray-600';
  }
}

export default function PropertyList({
  properties,
  ranked,
  selectedId,
  onSelect,
  watchedIds = [],
  onToggleWatchlist,
  loading = false,
}: PropertyListProps) {
  if (loading) {
    return (
      <div className="space-y-3 p-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="bg-white rounded-lg border border-gray-100 p-3 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
            <div className="h-3 bg-gray-200 rounded w-1/2 mb-2" />
            <div className="h-3 bg-gray-200 rounded w-1/4" />
          </div>
        ))}
      </div>
    );
  }

  // Use ranked order if available, otherwise use properties
  const displayItems: { property: Property; rank?: number; overall?: number }[] = ranked?.length
    ? ranked.map((r) => ({ property: r.property, rank: r.rank, overall: r.overall_score }))
    : properties.map((p) => ({ property: p, overall: p.score?.overall_score }));

  if (displayItems.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        No properties found
      </div>
    );
  }

  return (
    <div className="space-y-1.5 overflow-y-auto max-h-[calc(100vh-420px)] pr-1">
      {displayItems.map(({ property, rank, overall }) => {
        const isSelected = property.id === selectedId;
        const isWatched = watchedIds.includes(property.id);
        const displayScore = overall ?? property.score?.overall_score;

        return (
          <button
            key={property.id}
            onClick={() => onSelect(property)}
            className={`w-full text-left rounded-lg border p-3 transition-all ${
              isSelected
                ? 'border-indigo-400 bg-indigo-50 shadow-sm'
                : 'border-gray-100 bg-white hover:border-gray-200 hover:shadow-sm'
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {rank != null && (
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center">
                      {rank}
                    </span>
                  )}
                  <span className="text-sm font-medium text-gray-900 truncate">
                    {property.address}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-1.5">
                  <MapPin className="w-3 h-3" />
                  <span className="truncate">{property.neighborhood || 'Montgomery'}</span>
                </div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${typeBadge(property.property_type)}`}>
                    {property.property_type.replace('_', ' ')}
                  </span>
                  {property.is_vacant && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-red-100 text-red-700">
                      Vacant
                    </span>
                  )}
                  {property.is_city_owned && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-100 text-blue-700 flex items-center gap-0.5">
                      <Building2 className="w-2.5 h-2.5" />
                      City
                    </span>
                  )}
                </div>
              </div>
              <div className="flex flex-col items-end gap-1.5">
                {displayScore != null && (
                  <span className={`px-2 py-1 rounded-lg border text-sm font-bold ${scoreBg(displayScore)} ${scoreColor(displayScore)}`}>
                    {displayScore.toFixed(1)}
                  </span>
                )}
                {onToggleWatchlist && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleWatchlist(property.id);
                    }}
                    className="p-0.5 hover:scale-110 transition-transform"
                    title={isWatched ? 'Remove from watchlist' : 'Add to watchlist'}
                  >
                    <Star
                      className={`w-4 h-4 ${
                        isWatched ? 'fill-amber-400 text-amber-400' : 'text-gray-300 hover:text-amber-400'
                      }`}
                    />
                  </button>
                )}
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}
