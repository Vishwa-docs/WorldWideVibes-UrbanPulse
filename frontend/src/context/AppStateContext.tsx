import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import type { OpportunityRole, PersonaType, ScenarioType } from '../types';

type AppState = {
  activePersona: PersonaType;
  setActivePersona: (value: PersonaType) => void;
  togglePersona: () => void;
  activeScenario: ScenarioType;
  setActiveScenario: (value: ScenarioType) => void;
  activeRole: OpportunityRole;
  setActiveRole: (value: OpportunityRole) => void;
};

const AppStateContext = createContext<AppState | null>(null);

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [activePersona, setActivePersona] = useState<PersonaType>('city_console');
  const [activeScenario, setActiveScenario] = useState<ScenarioType>('general');
  const [activeRole, setActiveRole] = useState<OpportunityRole>('resident');

  // Auto-derive persona from active role
  useEffect(() => {
    setActivePersona(activeRole === 'entrepreneur' ? 'entrepreneur' : 'city_console');
  }, [activeRole]);

  const value = useMemo<AppState>(() => ({
    activePersona,
    setActivePersona,
    togglePersona: () => {
      setActivePersona(prev => (prev === 'city_console' ? 'entrepreneur' : 'city_console'));
    },
    activeScenario,
    setActiveScenario,
    activeRole,
    setActiveRole,
  }), [activePersona, activeScenario, activeRole]);

  return (
    <AppStateContext.Provider value={value}>
      {children}
    </AppStateContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAppState() {
  const ctx = useContext(AppStateContext);
  if (!ctx) {
    throw new Error('useAppState must be used inside AppStateProvider');
  }
  return ctx;
}
