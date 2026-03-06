import { Layers } from 'lucide-react';

interface LayerControlsProps {
  layers: Record<string, boolean>;
  onToggle: (layerId: string) => void;
}

const LAYER_OPTIONS = [
  { id: 'vacant', label: 'Vacant Lots', color: 'bg-red-400' },
  { id: 'city_owned', label: 'City-Owned', color: 'bg-blue-400' },
  { id: 'commercial', label: 'Commercial', color: 'bg-green-400' },
  { id: 'incidents', label: 'Incidents', color: 'bg-orange-400' },
  { id: 'equity_overlay', label: 'Equity Overlay', color: 'bg-purple-400' },
];

export default function LayerControls({ layers, onToggle }: LayerControlsProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-3">
      <div className="flex items-center gap-2 mb-2.5">
        <Layers className="w-4 h-4 text-indigo-600" />
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Map Layers</h3>
      </div>
      <div className="space-y-1.5">
        {LAYER_OPTIONS.map((layer) => (
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
    </div>
  );
}
