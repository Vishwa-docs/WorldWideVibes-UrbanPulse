import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  X,
  ChevronRight,
  ChevronLeft,
  Home,
  Map,
  Sparkles,
  DollarSign,
  Activity,
  Users,
  Briefcase,
  Building2,
  GraduationCap,
  Database,
  Globe,
  Zap,
} from 'lucide-react';

const STORAGE_KEY = 'urbanpulse_onboarding_seen';

interface Step {
  title: string;
  subtitle: string;
  description: string;
  icon: typeof Home;
  iconBg: string;
  features: string[];
  route?: string;
  routeLabel?: string;
}

const STEPS: Step[] = [
  {
    title: 'Welcome to UrbanPulse',
    subtitle: 'AI-Powered Civic Intelligence for Montgomery, AL',
    description:
      'UrbanPulse fuses 8 Montgomery Open Data endpoints, Bright Data web signals, US Census demographics, and Azure OpenAI into one civic-intelligence platform that delivers actionable, role-specific economic opportunity recommendations.',
    icon: Activity,
    iconBg: 'from-indigo-500 to-purple-500',
    features: [
      '8 ArcGIS REST endpoints — all live Montgomery data, zero mock',
      '4 Bright Data products — Web Scraper, SERP API, Web Unlocker, MCP Server',
      '31 Census ACS variables — workforce, education, commuting',
      'Azure OpenAI GPT-4o-2 with deterministic fallback',
    ],
  },
  {
    title: 'Opportunity Copilot',
    subtitle: 'Your AI-powered landing page',
    description:
      'Choose from 4 role-based lenses (Resident, Entrepreneur, City Staff, Education) and 5 scenarios (General, Grocery, Clinic, Daycare, Coworking). UrbanPulse automatically ranks properties and surfaces the top opportunities with full evidence and provenance.',
    icon: Home,
    iconBg: 'from-emerald-500 to-teal-500',
    features: [
      'Multi-objective scoring — Resident Fit, Business Opportunity, City Impact',
      'Auto-loaded property recommendations per role & scenario',
      'Signal change feed tracking 48-hour shifts',
      'Data Sources & Trust panel with source-level traceability',
    ],
    route: '/',
    routeLabel: 'Go to Copilot',
  },
  {
    title: 'Site Selection Workspace',
    subtitle: 'Interactive map with 14 data layers',
    description:
      'Explore Montgomery on an interactive Leaflet map with toggleable ArcGIS overlays — 311 requests, business licenses, foot traffic, vacant reports, code violations, opportunity zones, city-owned parcels, and building permits. Click any property for a detailed scorecard.',
    icon: Map,
    iconBg: 'from-blue-500 to-cyan-500',
    features: [
      '14 toggleable data layers from live Montgomery sources',
      'AI Agent Chat — ask natural-language questions about properties',
      'Watchlist & compare — save properties for side-by-side analysis',
      'CSV export for operational workflows',
    ],
    route: '/site',
    routeLabel: 'Go to Site Workspace',
  },
  {
    title: 'City Insights & Analytics',
    subtitle: 'Charts, web intelligence, and demographics',
    description:
      'Seven interactive Recharts visualizations covering business licenses by type, foot traffic hotspots, 311 requests, property scores, and workforce data. Plus a SERP-powered web intelligence panel, weather widget, and enhanced Census demographics.',
    icon: Sparkles,
    iconBg: 'from-purple-500 to-pink-500',
    features: [
      'Radar chart comparing business licenses vs foot traffic',
      'Web Intelligence — SERP search + URL scraper + Bright Data view',
      'Real-time weather from Open-Meteo',
      '31 Census ACS variables: education, commuting, transportation',
    ],
    route: '/insights',
    routeLabel: 'Go to Insights',
  },
  {
    title: 'Business Model',
    subtitle: 'Commercial viability & go-to-market',
    description:
      'UrbanPulse is designed as a city-agnostic SaaS platform. Adding a new city requires only a config file — zero code changes, < 1 week onboarding. View pricing tiers, market sizing, competitive landscape, 3-year revenue projections, and unit economics.',
    icon: DollarSign,
    iconBg: 'from-amber-500 to-orange-500',
    features: [
      'Starter $2K/mo, Pro $5K/mo, Enterprise $10K–15K/mo',
      '85% gross margins — public data = free COGS',
      'TAM: 19,500+ US municipalities, $105B muni IT market',
      'Year 3 projection: $4.3M ARR across 80 cities',
    ],
    route: '/business',
    routeLabel: 'Go to Business Model',
  },
];

const ROLE_ICONS = [
  { icon: Users, label: 'Residents', color: 'text-blue-400' },
  { icon: Briefcase, label: 'Entrepreneurs', color: 'text-emerald-400' },
  { icon: Building2, label: 'City Staff', color: 'text-amber-400' },
  { icon: GraduationCap, label: 'Education', color: 'text-purple-400' },
];

export default function WelcomeModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    const seen = localStorage.getItem(STORAGE_KEY);
    if (!seen) {
      // Small delay to let the page render first
      const timer = setTimeout(() => setIsOpen(true), 600);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleClose = () => {
    setIsOpen(false);
    localStorage.setItem(STORAGE_KEY, 'true');
  };

  const handleNext = () => {
    if (step < STEPS.length - 1) setStep(step + 1);
    else handleClose();
  };

  const handlePrev = () => {
    if (step > 0) setStep(step - 1);
  };

  if (!isOpen) return null;

  const currentStep = STEPS[step];
  const Icon = currentStep.icon;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300">
        {/* Header gradient bar */}
        <div className="h-1.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />

        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors z-10"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Step indicator */}
        <div className="px-8 pt-6 flex items-center gap-1.5">
          {STEPS.map((_, i) => (
            <button
              key={i}
              onClick={() => setStep(i)}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === step
                  ? 'w-8 bg-indigo-500'
                  : i < step
                  ? 'w-4 bg-indigo-300'
                  : 'w-4 bg-gray-200'
              }`}
            />
          ))}
          <span className="ml-auto text-xs text-gray-400 font-medium">
            {step + 1} / {STEPS.length}
          </span>
        </div>

        {/* Content */}
        <div className="px-8 py-6">
          <div className="flex items-start gap-4">
            <div
              className={`p-3 rounded-xl bg-gradient-to-br ${currentStep.iconBg} shadow-lg shrink-0`}
            >
              <Icon className="w-7 h-7 text-white" />
            </div>
            <div className="min-w-0">
              <h2 className="text-xl font-bold text-gray-900">{currentStep.title}</h2>
              <p className="text-sm text-indigo-600 font-medium mt-0.5">
                {currentStep.subtitle}
              </p>
            </div>
          </div>

          <p className="mt-4 text-sm text-gray-600 leading-relaxed">
            {currentStep.description}
          </p>

          {/* Role icons on first step */}
          {step === 0 && (
            <div className="mt-4 flex items-center gap-4 p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                4 Role Lenses
              </span>
              <div className="flex items-center gap-3">
                {ROLE_ICONS.map(({ icon: RIcon, label, color }) => (
                  <div key={label} className="flex items-center gap-1.5">
                    <RIcon className={`w-4 h-4 ${color}`} />
                    <span className="text-xs font-medium text-slate-700">{label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Feature list */}
          <div className="mt-4 space-y-2">
            {currentStep.features.map((feature, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <div className="mt-1 w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0" />
                <p className="text-sm text-gray-700">{feature}</p>
              </div>
            ))}
          </div>

          {/* Data source badges on first step */}
          {step === 0 && (
            <div className="mt-5 flex items-center gap-2 flex-wrap">
              {[
                { icon: Database, label: '8 ArcGIS Endpoints', color: 'bg-blue-50 text-blue-700 border-blue-200' },
                { icon: Globe, label: '4 Bright Data Products', color: 'bg-orange-50 text-orange-700 border-orange-200' },
                { icon: Users, label: '31 Census Variables', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
                { icon: Zap, label: 'Azure OpenAI', color: 'bg-purple-50 text-purple-700 border-purple-200' },
              ].map(({ icon: BIcon, label, color }) => (
                <span
                  key={label}
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${color}`}
                >
                  <BIcon className="w-3 h-3" />
                  {label}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-8 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {step > 0 && (
              <button
                onClick={handlePrev}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-200 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </button>
            )}
            {currentStep.route && (
              <Link
                to={currentStep.route}
                onClick={handleClose}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-indigo-600 hover:bg-indigo-50 transition-colors"
              >
                {currentStep.routeLabel}
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleClose}
              className="px-4 py-2 rounded-lg text-sm font-medium text-gray-500 hover:bg-gray-200 transition-colors"
            >
              Skip Tour
            </button>
            <button
              onClick={handleNext}
              className="inline-flex items-center gap-1.5 px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-semibold shadow-md hover:shadow-lg hover:from-indigo-700 hover:to-purple-700 transition-all"
            >
              {step === STEPS.length - 1 ? 'Get Started' : 'Next'}
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Export a helper to reset onboarding (useful for a "Show Tour" button)
export function resetOnboarding() {
  localStorage.removeItem(STORAGE_KEY);
}
