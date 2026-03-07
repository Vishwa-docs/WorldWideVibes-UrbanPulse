import { Layers, Database } from 'lucide-react';

interface LayerControlsProps {
  layers: Record<string, boolean>;
  onToggle: (layerId: string) => void;
}

const PROPERTY_LAYERS = [
  { id: 'vacant', label: 'Vacant Lots', color: 'bg-red-400' },
  { id: 'city_owned', label: 'City-Owned', color: 'bg-blue-400' },
  { id: 'commercial', label: 'Commercial', color: 'bg-green-400' },
  { id: 'incidents', label: 'Incidents', color: 'bg-orange-400' },
  { id: 'equity_overlay', label: 'Equity Overlay', color: 'bg-purple-400' },
  { id: 'demographics', label: 'Demographics', color: 'bg-indigo-400' },
];

const MONTGOMERY_LAYERS = [
  { id: 'service_requests', label: '311 Requests', color: 'bg-amber-400' },
  { id: 'foot_traffic', label: 'Foot Traffic', color: 'bg-violet-400' },
  { id: 'vacant_reports', label: 'Vacant/Blight Reports', color: 'bg-rose-300' },
  { id: 'business_licenses', label: 'Business Licenses', color: 'bg-emerald-400' },
];

export default function LayerControls({ layers, onToggle }: LayerControlsProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-3">
      <div className="flex items-center gap-2 mb-2.5">
        <Layers className="w-4 h-4 text-indigo-600" />
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Map Layers</h3>
      </div>
      <div className="space-y-1.5">
        {PROPERTY_LAYERS.map((layer) => (
          <label
            key={layer.id}
            className="flex items-center gap-2.5 text-sm text-gray-700 cursor-pointer hover:bg-gray-50 rounded-md px-1.5 py-1 transition-colors"
          >
            <input
              type="checkbox"
              checked={layers[layer.id] ?? true}
              onChange={() => onToggle(layer.id)}
              className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5"
            />
            <span className={`w-2.5 h-2.5 rounded-full ${layer.color}`} />
            <span className="text-xs">{layer.label}</span>
          </label>
        ))}
      </div>

      {/* Montgomery Open Data Layers */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center gap-2 mb-2">
          <Database className="w-3.5 h-3.5 text-emerald-600" />
          <h4 className="text-[10px] font-semibold text-emerald-700 uppercase tracking-wider">Montgomery Data</h4>
        </div>
        <div className="space-y-1.5">
          {MONTGOMERY_LAYERS.map((layer) => (
            <label
              key={layer.id}
              className="flex items-center gap-2.5 text-sm text-gray-700 cursor-pointer hover:bg-gray-50 rounded-md px-1.5 py-1 transition-colors"
            >
              <input
                type="checkbox"
                checked={layers[layer.id] ?? false}
                onChange={() => onToggle(layer.id)}
                className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 w-3.5 h-3.5"
              />
              <span className={`w-2.5 h-2.5 rounded-full ${layer.color}`} />
              <span className="text-xs">{layer.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
