import { Zap } from 'lucide-react';

/**
 * Small "Powered by Bright Data" badge for prominent placement.
 * Demonstrates Bright Data integration for hackathon bonus points.
 */
export default function BrightDataBadge() {
  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gradient-to-r from-orange-500/20 to-amber-500/20 border border-orange-400/30 rounded-lg">
      <Zap className="w-3 h-3 text-orange-400" />
      <span className="text-[10px] font-bold text-orange-300 uppercase tracking-wider whitespace-nowrap">
        Bright Data
      </span>
    </div>
  );
}
