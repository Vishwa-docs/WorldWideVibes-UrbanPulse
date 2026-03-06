import { Link, useLocation } from 'react-router-dom';
import { Activity, Map, GitCompareArrows, BookOpen } from 'lucide-react';
import PersonaToggle from '../Persona/PersonaToggle';
import type { PersonaType } from '../../types';

interface HeaderProps {
  activePersona: PersonaType;
  onTogglePersona: () => void;
}

const navItems = [
  { to: '/', label: 'Dashboard', icon: Map },
  { to: '/compare', label: 'Compare', icon: GitCompareArrows },
  { to: '/story', label: 'Story Mode', icon: BookOpen },
];

export default function Header({ activePersona, onTogglePersona }: HeaderProps) {
  const location = useLocation();

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-8">
        <Link to="/" className="flex items-center gap-2 group">
          <Activity className="w-7 h-7 text-indigo-600 group-hover:text-indigo-700 transition-colors" />
          <span className="text-xl font-bold text-gray-900 tracking-tight">
            Urban<span className="text-indigo-600">Pulse</span>
          </span>
        </Link>
        <nav className="flex items-center gap-1">
          {navItems.map(({ to, label, icon: Icon }) => {
            const isActive = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
      <PersonaToggle activePersona={activePersona} onToggle={onTogglePersona} />
    </header>
  );
}
