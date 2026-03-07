import { Star, ListFilter } from 'lucide-react';
import PropertyScorecard from '../Scorecards/PropertyScorecard';
import PropertyList from '../PropertyList/PropertyList';
import ScenarioSelector from '../Scenario/ScenarioSelector';
import LayerControls from '../Map/LayerControls';
import ExportButton from '../Export/ExportButton';
import AgentChat from '../Agent/AgentChat';
import type { Property, RankedPropertyItem, ScorecardResponse, PersonaType, ScenarioType } from '../../types';

interface SidebarProps {
  activePersona: PersonaType;
  activeScenario: ScenarioType;
  onSelectScenario: (s: ScenarioType) => void;
  properties: Property[];
  ranked: RankedPropertyItem[];
  selectedProperty: Property | null;
  onSelectProperty: (p: Property) => void;
  scorecard: ScorecardResponse | null;
  scorecardLoading: boolean;
  layers: Record<string, boolean>;
  onToggleLayer: (id: string) => void;
  watchedIds: number[];
  onToggleWatchlist: (id: number) => void;
  onAddToCompare: (id: number) => void;
  showWatchlistOnly: boolean;
  onToggleWatchlistFilter: () => void;
  propertiesLoading: boolean;
}

export default function Sidebar({
  activePersona,
  activeScenario,
  onSelectScenario,
  properties,
  ranked,
  selectedProperty,
  onSelectProperty,
  scorecard,
  scorecardLoading,
  layers,
  onToggleLayer,
  watchedIds,
  onToggleWatchlist,
  onAddToCompare,
  showWatchlistOnly,
  onToggleWatchlistFilter,
  propertiesLoading,
}: SidebarProps) {
  const filteredProperties = showWatchlistOnly
    ? properties.filter((p) => watchedIds.includes(p.id))
    : properties;

  const filteredRanked = showWatchlistOnly
    ? ranked.filter((r) => watchedIds.includes(r.property.id))
    : ranked;

  return (
    <aside className="w-[340px] bg-gray-50 border-r border-gray-200 flex flex-col overflow-hidden min-h-0">
      {/* Scenario Selector */}
      <div className="p-3 border-b border-gray-200">
        <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Scenario</p>
        <ScenarioSelector activeScenario={activeScenario} onSelect={onSelectScenario} />
      </div>

      {/* Scorecard for selected property */}
      {selectedProperty && (
        <div className="p-3 border-b border-gray-200 overflow-y-auto max-h-[40vh] flex-shrink-0">
          <PropertyScorecard
            property={selectedProperty}
            scorecard={scorecard}
            persona={activePersona}
            onAddToCompare={onAddToCompare}
            onToggleWatchlist={onToggleWatchlist}
            isWatched={watchedIds.includes(selectedProperty.id)}
            loading={scorecardLoading}
          />
        </div>
      )}

      {/* Property list header with filters */}
      <div className="px-3 pt-3 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ListFilter className="w-3.5 h-3.5 text-gray-400" />
          <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">
            Properties
          </h3>
          <span className="text-[10px] text-gray-400 bg-gray-200 px-1.5 py-0.5 rounded-full">
            {filteredProperties.length}
          </span>
        </div>
        <button
          onClick={onToggleWatchlistFilter}
          className={`flex items-center gap-1 text-xs px-2 py-1 rounded-md transition-colors ${
            showWatchlistOnly
              ? 'bg-amber-50 text-amber-600 border border-amber-200'
              : 'text-gray-400 hover:text-gray-600'
          }`}
        >
          <Star className={`w-3 h-3 ${showWatchlistOnly ? 'fill-amber-400' : ''}`} />
          <span className="hidden lg:inline">Starred</span>
        </button>
      </div>

      {/* Property List */}
      <div className="flex-1 overflow-y-auto px-3 pb-2">
        <PropertyList
          properties={filteredProperties}
          ranked={filteredRanked}
          selectedId={selectedProperty?.id}
          onSelect={onSelectProperty}
          watchedIds={watchedIds}
          onToggleWatchlist={onToggleWatchlist}
          loading={propertiesLoading}
        />
      </div>

      {/* Bottom section */}
      <div className="p-3 border-t border-gray-200 space-y-2 overflow-y-auto max-h-[50vh] flex-shrink-0">
        <AgentChat
          persona={activePersona}
          scenario={activeScenario}
          onPropertySelect={onSelectProperty}
        />
        <LayerControls layers={layers} onToggle={onToggleLayer} />
        <ExportButton scenario={activeScenario} persona={activePersona} />
      </div>
    </aside>
  );
}
