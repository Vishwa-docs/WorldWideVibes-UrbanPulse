import { useState, useCallback } from 'react';
import type { PersonaType, Persona } from '../types';

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
  const [activePersona, setActivePersona] = useState<PersonaType>('city_console');

  const togglePersona = useCallback(() => {
    setActivePersona(prev =>
      prev === 'city_console' ? 'entrepreneur' : 'city_console',
    );
  }, []);

  const selectPersona = useCallback((persona: PersonaType) => {
    setActivePersona(persona);
  }, []);

  return {
    activePersona,
    persona: PERSONAS[activePersona],
    togglePersona,
    selectPersona,
  };
}
