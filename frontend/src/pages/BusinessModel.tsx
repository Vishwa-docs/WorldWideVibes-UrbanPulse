import {
  DollarSign,
  TrendingUp,
  Building2,
  Users,
  Shield,
  Zap,
  BarChart3,
  Target,
  Globe,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';

/* ── Static data (matches docs/business-model.md) ────────────────────────── */

const MARKET_STATS = [
  { label: 'US Municipalities', value: '19,502', source: 'Census of Governments 2022' },
  { label: 'Cities with Open-Data Portals', value: '~3,200', source: 'data.gov catalog' },
  { label: 'Cities with ArcGIS Enterprise', value: '~8,000', source: 'Esri estimates' },
  { label: 'Annual US Municipal IT Spend', value: '$105 B', source: 'Gartner 2024' },
  { label: 'GovTech Market CAGR', value: '14.2%', source: 'MarketsAndMarkets 2024' },
];

const COMPETITORS = [
  {
    name: 'Esri ArcGIS Hub',
    what: 'Open-data portal + dashboards',
    cost: '$25K–$100K/yr',
    gap: 'No AI recommendations, no role-based copilot, no web-signal fusion',
  },
  {
    name: 'mySidewalk',
    what: 'Community data dashboards',
    cost: '$12K–$36K/yr',
    gap: 'Static reports, no real-time signals, no scenario-based scoring',
  },
  {
    name: 'UrbanFootprint',
    what: 'Land-use analytics',
    cost: '$50K–$150K/yr',
    gap: 'Infrastructure-heavy, expensive, no conversational AI layer',
  },
  {
    name: 'Placer.ai',
    what: 'Foot-traffic analytics',
    cost: '$25K–$100K/yr',
    gap: 'Single data source, no civic lens, no equity weighting',
  },
];

const TIERS = [
  {
    name: 'Starter',
    price: '$2,000',
    period: '/mo',
    annual: '$24K/yr',
    target: 'Small city or single department (< 100K pop)',
    features: ['1 city', '4 role lenses', '5 ArcGIS layers', 'Email support'],
    color: 'from-slate-500 to-slate-600',
    border: 'border-slate-200',
  },
  {
    name: 'Professional',
    price: '$5,000',
    period: '/mo',
    annual: '$60K/yr',
    target: 'Mid-size city (100K–500K pop)',
    features: [
      '1 city',
      'All layers + Bright Data signals',
      'Agent Chat',
      'Priority support',
    ],
    highlight: true,
    color: 'from-indigo-600 to-purple-600',
    border: 'border-indigo-300',
  },
  {
    name: 'Enterprise',
    price: '$10K–$15K',
    period: '/mo',
    annual: '$120K–$180K/yr',
    target: 'Large city, county, or regional authority',
    features: [
      'Multi-city deployment',
      'Custom integrations',
      'SSO & SLA',
      'Dedicated CSM',
    ],
    color: 'from-purple-600 to-pink-600',
    border: 'border-purple-200',
  },
];

const PROJECTIONS = [
  { year: 'Y1', cities: 5, avgArr: '$36K', revenue: '$180K', driver: 'Montgomery launch + 4 pilot cities' },
  { year: 'Y2', cities: 25, avgArr: '$48K', revenue: '$1.2M', driver: 'Alabama expansion + ArcGIS Hub adopters' },
  { year: 'Y3', cities: 80, avgArr: '$54K', revenue: '$4.3M', driver: 'National rollout + enterprise tier' },
];

const UNIT_ECONOMICS = [
  { label: 'Cloud hosting per city', value: '~$150/mo' },
  { label: 'Bright Data per city', value: '~$200/mo' },
  { label: 'Azure OpenAI per city', value: '~$100/mo' },
  { label: 'Total COGS per city', value: '~$450/mo', bold: true },
  { label: 'Gross margin (Pro tier)', value: '91%', bold: true },
  { label: 'Blended gross margin', value: '~85%', bold: true },
];

const GTM_PHASES = [
  {
    phase: 'Phase 1',
    title: 'Hackathon → Pilot',
    period: 'Q1–Q3 2026',
    items: [
      'Montgomery as reference customer',
      '4 additional pilot cities from GenAI.Works network',
      'Target ArcGIS Hub cities — fastest integration path',
    ],
  },
  {
    phase: 'Phase 2',
    title: 'Alabama Expansion',
    period: 'Q3 2026 – Q1 2027',
    items: [
      'Birmingham, Huntsville, Mobile, Tuscaloosa',
      'Partner with Alabama League of Municipalities',
      'Conference presence: NLC, ICMA, Smart Cities Connect',
    ],
  },
  {
    phase: 'Phase 3',
    title: 'National Scale',
    period: '2027+',
    items: [
      'Self-serve onboarding: paste ArcGIS portal URL → auto-discover',
      'Esri ArcGIS Marketplace listing',
      'Multi-city dashboards for county / regional agencies',
    ],
  },
];

/* ── Component ───────────────────────────────────────────────────────────── */

export default function BusinessModel() {
  return (
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-6 space-y-8">
        {/* Hero */}
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 rounded-xl p-6 shadow-lg">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-white/10 rounded-lg">
              <DollarSign className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white mb-1">
                Business Model & Commercial Potential
              </h1>
              <p className="text-indigo-100 text-sm leading-relaxed max-w-3xl">
                UrbanPulse enters the <strong>$105 B municipal IT market</strong> with an
                AI-powered civic-intelligence platform that undercuts Esri and mySidewalk
                while adding web-signal fusion and role-based recommendations.
              </p>
            </div>
          </div>
        </div>

        {/* Market Stats */}
        <section>
          <SectionHeader icon={Globe} title="The Market" />
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {MARKET_STATS.map((s) => (
              <div
                key={s.label}
                className="bg-white rounded-lg border border-gray-200 p-4 text-center shadow-sm"
              >
                <p className="text-2xl font-bold text-indigo-600">{s.value}</p>
                <p className="text-xs text-gray-600 mt-1 font-medium">{s.label}</p>
                <p className="text-[10px] text-gray-400 mt-0.5">{s.source}</p>
              </div>
            ))}
          </div>
          <p className="mt-3 text-sm text-gray-600">
            Immediate addressable market: <strong>~3,200 US cities</strong> already
            publishing open data — they have the infrastructure UrbanPulse plugs into
            with zero new hardware.
          </p>
        </section>

        {/* Competitive Landscape */}
        <section>
          <SectionHeader icon={Target} title="Competitive Landscape" />
          <div className="overflow-x-auto">
            <table className="w-full text-sm bg-white rounded-lg border border-gray-200 shadow-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Solution</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">What It Does</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Annual Cost</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Gap UrbanPulse Fills</th>
                </tr>
              </thead>
              <tbody>
                {COMPETITORS.map((c) => (
                  <tr key={c.name} className="border-b last:border-0 border-gray-100">
                    <td className="px-4 py-3 font-medium text-gray-900">{c.name}</td>
                    <td className="px-4 py-3 text-gray-600">{c.what}</td>
                    <td className="px-4 py-3 text-gray-600 font-mono text-xs">{c.cost}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{c.gap}</td>
                  </tr>
                ))}
                <tr className="bg-indigo-50">
                  <td className="px-4 py-3 font-bold text-indigo-700">UrbanPulse</td>
                  <td className="px-4 py-3 text-indigo-600 font-medium">
                    AI civic-intelligence + web signals
                  </td>
                  <td className="px-4 py-3 text-indigo-700 font-mono text-xs font-bold">
                    $24K–$60K/yr
                  </td>
                  <td className="px-4 py-3 text-indigo-600 text-xs font-medium">
                    All-in-one: live city data + web scraping + AI copilot + equity scoring
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Pricing Tiers */}
        <section>
          <SectionHeader icon={DollarSign} title="Pricing Tiers" />
          <div className="grid md:grid-cols-3 gap-4">
            {TIERS.map((tier) => (
              <div
                key={tier.name}
                className={`bg-white rounded-xl border-2 ${tier.border} p-5 shadow-sm relative ${
                  tier.highlight ? 'ring-2 ring-indigo-300 ring-offset-2' : ''
                }`}
              >
                {tier.highlight && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                    Most Popular
                  </span>
                )}
                <div
                  className={`inline-block bg-gradient-to-r ${tier.color} text-white text-xs font-bold px-3 py-1 rounded-full mb-3`}
                >
                  {tier.name}
                </div>
                <div className="flex items-baseline gap-1 mb-1">
                  <span className="text-3xl font-bold text-gray-900">{tier.price}</span>
                  <span className="text-gray-400 text-sm">{tier.period}</span>
                </div>
                <p className="text-xs text-gray-400 mb-3">{tier.annual}</p>
                <p className="text-sm text-gray-600 mb-4">{tier.target}</p>
                <ul className="space-y-2">
                  {tier.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-gray-700">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-4 bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
            <p className="text-sm text-gray-700">
              <strong>Why these numbers work:</strong> Esri ArcGIS Hub Premium costs cities $25K–$100K/yr
              for dashboards with <em>no AI</em>. UrbanPulse's $24K–$60K/yr price{' '}
              <strong>undercuts Esri</strong> while adding an AI copilot + web signals.
              Montgomery's Economic Development budget was <strong>$1.2M</strong> in FY2024 —
              UrbanPulse Pro at $60K/yr = 5% of budget.
            </p>
          </div>
        </section>

        {/* Revenue Projections */}
        <section>
          <SectionHeader icon={TrendingUp} title="3-Year Revenue Projections" />
          <div className="grid md:grid-cols-3 gap-4">
            {PROJECTIONS.map((p) => (
              <div
                key={p.year}
                className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-lg font-bold text-gray-900">{p.year}</span>
                  <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-1 rounded-full font-medium">
                    {p.cities} cities
                  </span>
                </div>
                <p className="text-3xl font-bold text-indigo-600 mb-1">{p.revenue}</p>
                <p className="text-xs text-gray-400 mb-2">
                  Avg. ARR/city: {p.avgArr}
                </p>
                <div className="flex items-start gap-1.5">
                  <ArrowRight className="w-3.5 h-3.5 text-gray-400 mt-0.5 flex-shrink-0" />
                  <p className="text-xs text-gray-600">{p.driver}</p>
                </div>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-gray-500">
            Assumptions: 60% Starter / 30% Professional / 10% Enterprise mix by Y3. 90% annual retention.
          </p>
        </section>

        {/* Unit Economics */}
        <section>
          <SectionHeader icon={BarChart3} title="Unit Economics" />
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="grid grid-cols-2 divide-x divide-gray-100">
              <div className="p-5">
                <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  Cost Structure (per city)
                </h4>
                <ul className="space-y-2">
                  {UNIT_ECONOMICS.map((item) => (
                    <li
                      key={item.label}
                      className={`flex justify-between text-sm ${
                        item.bold
                          ? 'font-bold text-gray-900 border-t border-gray-200 pt-2'
                          : 'text-gray-600'
                      }`}
                    >
                      <span>{item.label}</span>
                      <span className="font-mono">{item.value}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="p-5 flex flex-col items-center justify-center bg-gradient-to-br from-emerald-50 to-indigo-50">
                <p className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-indigo-600">
                  85%
                </p>
                <p className="text-sm font-semibold text-gray-700 mt-2">
                  Blended Gross Margin
                </p>
                <p className="text-xs text-gray-500 mt-1 text-center max-w-xs">
                  Most data sources (ArcGIS, Census, Open-Meteo) are free &amp; public.
                  Value is in the intelligence layer, not data acquisition.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Go-to-Market */}
        <section>
          <SectionHeader icon={Zap} title="Go-to-Market Strategy" />
          <div className="grid md:grid-cols-3 gap-4">
            {GTM_PHASES.map((phase) => (
              <div
                key={phase.phase}
                className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-bold">
                    {phase.phase}
                  </span>
                  <span className="text-xs text-gray-400">{phase.period}</span>
                </div>
                <h4 className="text-sm font-bold text-gray-900 mb-3">{phase.title}</h4>
                <ul className="space-y-2">
                  {phase.items.map((item) => (
                    <li
                      key={item}
                      className="flex items-start gap-2 text-xs text-gray-600"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mt-0.5 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Architecture Supports Scale */}
        <section>
          <SectionHeader icon={Building2} title="Why the Architecture Supports This" />
          <div className="grid sm:grid-cols-2 gap-3">
            {[
              {
                icon: Shield,
                title: 'Config-driven city setup',
                desc: 'config/cities/ directory holds per-city endpoint URLs, Census FIPS codes, and map bounds. Adding a new city = one config file, zero code changes.',
              },
              {
                icon: Users,
                title: 'Standard data contracts',
                desc: 'The scoring engine works on normalized schemas, not Montgomery-specific field names.',
              },
              {
                icon: Zap,
                title: 'Modular data connectors',
                desc: 'ArcGIS, Census, Bright Data, and Weather are separate services. Any can be swapped or extended.',
              },
              {
                icon: Globe,
                title: 'Universal role-based model',
                desc: 'The 4-role model (Resident, Entrepreneur, City Staff, Education) is universal to municipal governance.',
              },
            ].map((item) => (
              <div
                key={item.title}
                className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm flex gap-3"
              >
                <div className="p-2 bg-indigo-50 rounded-lg h-fit">
                  <item.icon className="w-4 h-4 text-indigo-600" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">{item.title}</h4>
                  <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 bg-indigo-50 rounded-lg border border-indigo-200 p-4">
            <p className="text-sm text-indigo-800 font-medium">
              Time to onboard a new city: <strong>&lt; 1 week</strong> (estimated),
              assuming the city has an ArcGIS open data portal.
            </p>
          </div>
        </section>

        {/* Bottom summary */}
        <section className="bg-gradient-to-r from-slate-800 to-indigo-900 rounded-xl p-6 shadow-lg">
          <h3 className="text-lg font-bold text-white mb-3">Summary</h3>
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { stat: '$24K–$60K/yr', desc: 'Undercuts Esri Hub & mySidewalk' },
              { stat: '85%', desc: 'Blended gross margin' },
              { stat: '$4.3M ARR', desc: 'Year 3 projection (80 cities)' },
              { stat: '< 1 week', desc: 'New city onboarding time' },
            ].map((s) => (
              <div key={s.stat} className="text-center">
                <p className="text-2xl font-bold text-white">{s.stat}</p>
                <p className="text-xs text-indigo-200 mt-1">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

/* ── Helpers ─────────────────────────────────────────────────────────────── */

function SectionHeader({
  icon: Icon,
  title,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
}) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <Icon className="w-5 h-5 text-indigo-600" />
      <h2 className="text-lg font-bold text-gray-900">{title}</h2>
    </div>
  );
}
