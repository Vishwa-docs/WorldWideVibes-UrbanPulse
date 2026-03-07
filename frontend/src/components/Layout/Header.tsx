import { Link, useLocation } from 'react-router-dom';
import { Activity, Map, GitCompareArrows, BookOpen, Sparkles } from 'lucide-react';
import PersonaToggle from '../Persona/PersonaToggle';
import BrightDataBadge from './BrightDataBadge';
import type { PersonaType } from '../../types';

interface HeaderProps {
  activePersona: PersonaType;
  onTogglePersona: () => void;
}

const navItems = [
  { to: '/', label: 'Dashboard', icon: Map },
  { to: '/compare', label: 'Compare', icon: GitCompareArrows },
  { to: '/story', label: 'Story Mode', icon: BookOpen },
  { to: '/insights', label: 'Insights', icon: Sparkles },
];

export default function Header({ activePersona, onTogglePersona }: HeaderProps) {
  const location = useLocation();

  return (
    <header className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 px-6 py-3 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-8">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="p-1.5 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg shadow-md group-hover:shadow-indigo-500/30 transition-shadow">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">
            Urban<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">Pulse</span>
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
                    ? 'bg-white/15 text-white shadow-sm'
                    : 'text-indigo-200 hover:bg-white/10 hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="flex items-center gap-3">
        <BrightDataBadge />
        <PersonaToggle activePersona={activePersona} onToggle={onTogglePersona} />
      </div>
    </header>
  );
}
