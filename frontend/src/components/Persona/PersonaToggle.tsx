import { Building2, Briefcase } from 'lucide-react';
import type { PersonaType } from '../../types';

interface PersonaToggleProps {
  activePersona: PersonaType;
  onToggle: () => void;
}

export default function PersonaToggle({ activePersona, onToggle }: PersonaToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="flex items-center gap-1 bg-gray-100 rounded-full p-1 transition-colors hover:bg-gray-200"
    >
      <span
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
          activePersona === 'city_console'
            ? 'bg-indigo-600 text-white shadow-sm'
            : 'text-gray-600'
        }`}
      >
        <Building2 className="w-4 h-4" />
        City Console
      </span>
      <span
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
          activePersona === 'entrepreneur'
            ? 'bg-indigo-600 text-white shadow-sm'
            : 'text-gray-600'
        }`}
      >
        <Briefcase className="w-4 h-4" />
        Entrepreneur Studio
      </span>
    </button>
  );
}
