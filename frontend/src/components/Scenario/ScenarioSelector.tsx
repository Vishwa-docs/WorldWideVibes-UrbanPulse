import type { ScenarioType } from '../../types';
import { SCENARIOS } from '../../hooks/useScenario';

interface ScenarioSelectorProps {
  activeScenario: ScenarioType;
  onSelect: (scenario: ScenarioType) => void;
}

export default function ScenarioSelector({ activeScenario, onSelect }: ScenarioSelectorProps) {
  return (
    <div className="flex gap-1.5 flex-wrap">
      {SCENARIOS.map((s) => {
        const isActive = s.id === activeScenario;
        return (
          <button
            key={s.id}
            onClick={() => onSelect(s.id)}
            title={s.description}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${
              isActive
                ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300 hover:text-indigo-600'
            }`}
          >
            <span className="text-sm">{s.icon}</span>
            <span>{s.name}</span>
          </button>
        );
      })}
    </div>
  );
}
