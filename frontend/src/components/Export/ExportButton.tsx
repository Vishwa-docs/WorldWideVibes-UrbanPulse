import { Download } from 'lucide-react';
import { exportCSV } from '../../services/api';
import type { ScenarioType, PersonaType } from '../../types';

interface ExportButtonProps {
  scenario: ScenarioType;
  persona: PersonaType;
}

export default function ExportButton({ scenario, persona }: ExportButtonProps) {
  return (
    <button
      onClick={() => exportCSV(scenario, persona)}
      className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-colors w-full justify-center"
    >
      <Download className="w-3.5 h-3.5" />
      Export CSV
    </button>
  );
}
