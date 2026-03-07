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
      className="flex items-center gap-1 bg-white/10 rounded-full p-1 transition-colors hover:bg-white/15"
    >
      <span
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
          activePersona === 'city_console'
            ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-sm'
            : 'text-indigo-200'
        }`}
      >
        <Building2 className="w-4 h-4" />
        City Console
      </span>
      <span
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
          activePersona === 'entrepreneur'
            ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-sm'
            : 'text-indigo-200'
        }`}
      >
        <Briefcase className="w-4 h-4" />
        Entrepreneur Studio
      </span>
    </button>
  );
}
