import { useCallback } from 'react';
import type { PersonaType, Persona } from '../types';
import { useAppState } from '../context/AppStateContext';

export const PERSONAS: Record<PersonaType, Persona> = {
  city_console: {
    type: 'city_console',
    label: 'City Console',
    description: 'For city planners and economic development staff',
    icon: 'building',
  },
  entrepreneur: {
    type: 'entrepreneur',
    label: 'Entrepreneur Studio',
    description: 'For small businesses and community organizations',
    icon: 'briefcase',
  },
};

export function usePersona() {
  const { activePersona, togglePersona, setActivePersona } = useAppState();
  const selectPersona = useCallback((persona: PersonaType) => setActivePersona(persona), [setActivePersona]);

  return {
    activePersona,
    persona: PERSONAS[activePersona],
    togglePersona,
    selectPersona,
  };
}
