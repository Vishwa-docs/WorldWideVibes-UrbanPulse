import { useCallback } from 'react';
import type { ScenarioType, Scenario } from '../types';
import { useAppState } from '../context/AppStateContext';

export const SCENARIOS: Scenario[] = [
  { id: 'general', name: 'General', description: 'Balanced scoring for all factors', icon: '🎯' },
  { id: 'grocery', name: 'Local Grocery', description: 'Prioritizes equity and competition gaps', icon: '🛒' },
  { id: 'clinic', name: 'Health Clinic', description: 'Emphasizes equity and service gaps', icon: '🏥' },
  { id: 'daycare', name: 'Daycare Center', description: 'Focuses on safety and foot traffic', icon: '👶' },
  { id: 'coworking', name: 'Coworking Hub', description: 'Values activity and foot traffic', icon: '💻' },
];

export function useScenario() {
  const { activeScenario, setActiveScenario } = useAppState();
  const selectScenario = useCallback((scenario: ScenarioType) => setActiveScenario(scenario), [setActiveScenario]);

  const currentScenario = SCENARIOS.find(s => s.id === activeScenario)!;

  return { activeScenario, currentScenario, scenarios: SCENARIOS, selectScenario };
}
