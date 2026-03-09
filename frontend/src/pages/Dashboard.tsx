import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import MapView from '../components/Map/MapView';
import MapErrorBoundary from '../components/Map/MapErrorBoundary';
import Sidebar from '../components/Layout/Sidebar';
import LiveDataBar from '../components/Layout/LiveDataBar';
import DemographicsPanel from '../components/Insights/DemographicsPanel';
import { useProperties } from '../hooks/useProperties';
import { useScenario } from '../hooks/useScenario';
import { useWatchlist } from '../hooks/useWatchlist';
import { fetchScorecard } from '../services/api';
import type { PersonaType, Property, ScorecardResponse } from '../types';
import { MapPin, TrendingUp, Building2, AlertTriangle, Users } from 'lucide-react';

interface DashboardProps {
  activePersona: PersonaType;
}

export default function Dashboard({ activePersona }: DashboardProps) {
  const { activeScenario, selectScenario } = useScenario();
  const { properties, ranked, loading: propertiesLoading } = useProperties(activePersona, activeScenario);
  const { items: watchlistItems, add: addWatch, remove: removeWatch } = useWatchlist(activePersona);

  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [scorecard, setScorecard] = useState<ScorecardResponse | null>(null);
  const [scorecardLoading, setScorecardLoading] = useState(false);
  const [showWatchlistOnly, setShowWatchlistOnly] = useState(false);
  const [compareIds, setCompareIds] = useState<number[]>([]);
  const [layers, setLayers] = useState<Record<string, boolean>>({
    vacant: true,
    city_owned: true,
    commercial: true,
    incidents: true,
    equity_overlay: false,
    demographics: false,
    service_requests: false,
    foot_traffic: false,
    vacant_reports: false,
    business_licenses: false,
    code_violations: false,
    opportunity_zones: false,
    city_owned_properties: false,
    building_permits: false,
  });

  const watchedIds = watchlistItems.map((w) => w.property_id);

  // Load scorecard when property selected
  useEffect(() => {
    if (!selectedProperty) {
      setScorecard(null);
      return;
    }
    let cancelled = false;
    setScorecardLoading(true);
    fetchScorecard(selectedProperty.id)
      .then((data) => {
        if (!cancelled) setScorecard(data);
      })
      .catch(() => {
        if (!cancelled) setScorecard(null);
      })
      .finally(() => {
        if (!cancelled) setScorecardLoading(false);
      });
    return () => { cancelled = true; };
  }, [selectedProperty]);

  const handleToggleWatchlist = useCallback(
    async (propertyId: number) => {
      const item = watchlistItems.find((w) => w.property_id === propertyId);
      if (item) {
        await removeWatch(item.id);
      } else {
        await addWatch(propertyId);
      }
    },
    [watchlistItems, addWatch, removeWatch],
  );

  const handleAddToCompare = useCallback((id: number) => {
    setCompareIds((prev) => {
      if (prev.includes(id)) return prev;
      if (prev.length >= 3) return prev;
      return [...prev, id];
    });
  }, []);

  const handleToggleLayer = useCallback((layerId: string) => {
    setLayers((prev) => ({ ...prev, [layerId]: !prev[layerId] }));
  }, []);

  // KPI stats
  const totalProperties = properties.length;
  const vacantCount = properties.filter((p) => p.is_vacant).length;
  const cityOwnedCount = properties.filter((p) => p.is_city_owned).length;
  const avgScore = properties.length > 0
    ? properties.reduce((sum, p) => sum + (p.score?.overall_score || 0), 0) / properties.length
    : 0;

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {/* Live Data Status Bar */}
      <LiveDataBar />

      {/* KPI Bar */}
      <div className="bg-white border-b border-gray-200 px-6 py-2.5 flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-50">
            <MapPin className="w-4 h-4 text-indigo-600" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Properties</p>
            <p className="text-sm font-bold text-gray-900">{totalProperties}</p>
          </div>
        </div>
        <div className="w-px h-8 bg-gray-200" />
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-red-50">
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Vacant</p>
            <p className="text-sm font-bold text-gray-900">{vacantCount}</p>
          </div>
        </div>
        <div className="w-px h-8 bg-gray-200" />
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-50">
            <Building2 className="w-4 h-4 text-blue-500" />
          </div>
          <div>
            <p className="text-xs text-gray-500">City-Owned</p>
            <p className="text-sm font-bold text-gray-900">{cityOwnedCount}</p>
          </div>
        </div>
        <div className="w-px h-8 bg-gray-200" />
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-50">
            <TrendingUp className="w-4 h-4 text-emerald-500" />
          </div>
          <div>
            <p className="text-xs text-gray-500">Avg Score</p>
            <p className="text-sm font-bold text-gray-900">{avgScore.toFixed(1)}</p>
          </div>
        </div>
        {compareIds.length > 0 && (
          <>
            <div className="w-px h-8 bg-gray-200" />
            <Link
              to="/compare"
              className="text-xs font-medium text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-lg hover:bg-indigo-100 transition-colors"
            >
              Compare ({compareIds.length})
            </Link>
          </>
        )}
        <div className="ml-auto">
          <Link
            to="/insights"
            className="flex items-center gap-1.5 text-xs font-medium text-purple-600 bg-purple-50 px-3 py-1.5 rounded-lg hover:bg-purple-100 transition-colors border border-purple-200"
          >
            <Users className="w-3.5 h-3.5" />
            City Insights
          </Link>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activePersona={activePersona}
          activeScenario={activeScenario}
          onSelectScenario={selectScenario}
          properties={properties}
          ranked={ranked}
          selectedProperty={selectedProperty}
          onSelectProperty={setSelectedProperty}
          scorecard={scorecard}
          scorecardLoading={scorecardLoading}
          layers={layers}
          onToggleLayer={handleToggleLayer}
          watchedIds={watchedIds}
          onToggleWatchlist={handleToggleWatchlist}
          onAddToCompare={handleAddToCompare}
          showWatchlistOnly={showWatchlistOnly}
          onToggleWatchlistFilter={() => setShowWatchlistOnly(!showWatchlistOnly)}
          propertiesLoading={propertiesLoading}
        />
        <main className="flex-1 relative">
          <MapErrorBoundary>
            <MapView
              properties={properties}
              selectedProperty={selectedProperty}
              onSelectProperty={setSelectedProperty}
              layers={layers}
              incidents={scorecard?.nearby_incidents}
            />
          </MapErrorBoundary>
          {/* Demographics overlay panel */}
          {layers.demographics && (
            <div className="absolute top-4 left-4 z-[1000] w-80">
              <DemographicsPanel
                lat={selectedProperty?.latitude}
                lng={selectedProperty?.longitude}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
