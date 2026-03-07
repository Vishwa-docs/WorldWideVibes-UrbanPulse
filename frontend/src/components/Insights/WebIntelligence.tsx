import { useState, useEffect } from 'react';
import {
  Search, Globe, Zap, ExternalLink, Loader2, ChevronDown, ChevronUp,
  FileText, Shield, Radio, Bot,
} from 'lucide-react';
import {
  searchSerp,
  scrapeUrl,
  fetchBrightDataCapabilities,
} from '../../services/api';
import type { SerpResult, SerpResponse, BrightDataCapabilities } from '../../types';

/* ── Quick-search presets for Montgomery ──────────────────────────────── */
const PRESET_SEARCHES = [
  { label: 'Grocery stores', query: 'grocery stores Montgomery AL' },
  { label: 'Daycare centers', query: 'daycare centers Montgomery AL' },
  { label: 'Co-working spaces', query: 'coworking spaces Montgomery AL' },
  { label: 'New restaurants', query: 'new restaurants opening Montgomery Alabama 2026' },
  { label: 'Business grants', query: 'small business grants Montgomery Alabama' },
  { label: 'Vacant properties', query: 'commercial real estate vacant Montgomery AL' },
];

const PRODUCT_ICONS: Record<string, typeof Globe> = {
  'Web Scraper (Datasets API)': Globe,
  'SERP API': Search,
  'Web Unlocker': Shield,
  'MCP Server': Bot,
};

const STATUS_COLORS: Record<string, string> = {
  active: 'bg-emerald-100 text-emerald-700',
  simulated: 'bg-amber-100 text-amber-700',
  documented: 'bg-sky-100 text-sky-700',
};

export default function WebIntelligence() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SerpResponse | null>(null);
  const [searching, setSearching] = useState(false);
  const [capabilities, setCapabilities] = useState<BrightDataCapabilities | null>(null);
  const [showCaps, setShowCaps] = useState(false);
  const [scrapeTarget, setScrapeTarget] = useState('');
  const [scrapeContent, setScrapeContent] = useState<string | null>(null);
  const [scraping, setScraping] = useState(false);

  useEffect(() => {
    fetchBrightDataCapabilities().then(setCapabilities).catch(() => {});
  }, []);

  const handleSearch = async (searchQuery?: string) => {
    const q = searchQuery || query;
    if (!q.trim()) return;
    setSearching(true);
    setResults(null);
    try {
      const data = await searchSerp(q);
      setResults(data);
    } catch {
      setResults({
        query: q, engine: 'google', location: 'Montgomery,Alabama,United States',
        result_count: 0, results: [], source: 'error', is_live: false,
        fetched_at: new Date().toISOString(), error: 'Search failed',
      });
    } finally {
      setSearching(false);
    }
  };

  const handleScrape = async () => {
    if (!scrapeTarget.trim()) return;
    setScraping(true);
    setScrapeContent(null);
    try {
      const data = await scrapeUrl(scrapeTarget, 4000);
      setScrapeContent(data.content);
    } catch {
      setScrapeContent('Failed to scrape URL.');
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm mb-6 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-amber-500 px-5 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Web Intelligence</h2>
              <p className="text-xs text-orange-100">
                Powered by Bright Data — SERP API, Web Unlocker, Datasets &amp; MCP
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowCaps(!showCaps)}
            className="flex items-center gap-1 px-2.5 py-1 bg-white/20 rounded-lg text-xs text-white
                       hover:bg-white/30 transition-colors"
          >
            {capabilities?.products.length ?? 4} Products
            {showCaps ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Capabilities accordion */}
      {showCaps && capabilities && (
        <div className="border-b border-gray-200 bg-gray-50 px-5 py-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {capabilities.products.map((p) => {
              const Icon = PRODUCT_ICONS[p.name] || Globe;
              return (
                <div key={p.name} className="flex items-start gap-2.5 p-2.5 bg-white rounded-lg border border-gray-100">
                  <Icon className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-semibold text-gray-800 truncate">{p.name}</span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium ${STATUS_COLORS[p.status] || 'bg-gray-100 text-gray-600'}`}>
                        {p.status}
                      </span>
                    </div>
                    <p className="text-[10px] text-gray-500 mt-0.5">{p.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="p-5 space-y-4">
        {/* SERP Search */}
        <div>
          <label className="flex items-center gap-1.5 text-xs font-semibold text-gray-700 mb-2">
            <Search className="w-3.5 h-3.5 text-orange-500" />
            Local Search Intelligence (SERP API)
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search Montgomery, AL business landscape..."
              className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg
                         focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none"
            />
            <button
              onClick={() => handleSearch()}
              disabled={searching || !query.trim()}
              className="px-4 py-2 bg-orange-500 text-white text-sm font-medium rounded-lg
                         hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed
                         transition-colors flex items-center gap-1.5"
            >
              {searching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
              Search
            </button>
          </div>

          {/* Preset searches */}
          <div className="flex flex-wrap gap-1.5 mt-2">
            {PRESET_SEARCHES.map((preset) => (
              <button
                key={preset.label}
                onClick={() => { setQuery(preset.query); handleSearch(preset.query); }}
                className="px-2.5 py-1 text-[10px] font-medium text-orange-700 bg-orange-50
                           border border-orange-200 rounded-full hover:bg-orange-100 transition-colors"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* Search Results */}
        {results && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-3 py-2 bg-gray-50 border-b border-gray-200">
              <span className="text-xs font-medium text-gray-600">
                {results.result_count} results for "{results.query}"
              </span>
              <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium ${
                results.is_live ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
              }`}>
                {results.is_live ? 'Live' : 'Simulated'}
              </span>
            </div>
            <div className="divide-y divide-gray-100 max-h-64 overflow-y-auto">
              {results.results.map((r: SerpResult, i: number) => (
                <div key={i} className="px-3 py-2.5 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start gap-2">
                    <span className="text-[9px] font-bold text-gray-400 mt-0.5">{r.position}</span>
                    <div className="min-w-0 flex-1">
                      <a
                        href={r.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-indigo-600 hover:text-indigo-800
                                   flex items-center gap-1 truncate"
                      >
                        {r.title}
                        <ExternalLink className="w-3 h-3 flex-shrink-0" />
                      </a>
                      <p className="text-[11px] text-gray-500 mt-0.5 line-clamp-2">{r.description}</p>
                      <p className="text-[9px] text-gray-400 mt-0.5 truncate">{r.url}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Divider */}
        <div className="border-t border-gray-200" />

        {/* Web Scraper */}
        <div>
          <label className="flex items-center gap-1.5 text-xs font-semibold text-gray-700 mb-2">
            <FileText className="w-3.5 h-3.5 text-orange-500" />
            Web Page Scraper (Web Unlocker API)
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={scrapeTarget}
              onChange={(e) => setScrapeTarget(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleScrape()}
              placeholder="https://example.com/page-to-scrape"
              className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg
                         focus:ring-2 focus:ring-orange-400 focus:border-orange-400 outline-none"
            />
            <button
              onClick={handleScrape}
              disabled={scraping || !scrapeTarget.trim()}
              className="px-4 py-2 bg-orange-500 text-white text-sm font-medium rounded-lg
                         hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed
                         transition-colors flex items-center gap-1.5"
            >
              {scraping ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Globe className="w-3.5 h-3.5" />}
              Scrape
            </button>
          </div>
          <p className="text-[10px] text-gray-400 mt-1">
            Extracts clean markdown from any public webpage — handles CAPTCHAs, anti-bot, and dynamic content.
          </p>
        </div>

        {/* Scrape Results */}
        {scrapeContent && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="px-3 py-2 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
              <span className="text-xs font-medium text-gray-600 truncate">
                Scraped: {scrapeTarget}
              </span>
              <button
                onClick={() => setScrapeContent(null)}
                className="text-[10px] text-gray-400 hover:text-gray-600"
              >
                Clear
              </button>
            </div>
            <pre className="px-3 py-3 text-xs text-gray-700 bg-gray-50 max-h-48 overflow-y-auto whitespace-pre-wrap font-mono leading-relaxed">
              {scrapeContent}
            </pre>
          </div>
        )}

        {/* MCP Server note */}
        <div className="flex items-start gap-2.5 p-3 bg-sky-50 rounded-lg border border-sky-200">
          <Radio className="w-4 h-4 text-sky-500 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-xs font-semibold text-sky-800">MCP Server Integration</p>
            <p className="text-[10px] text-sky-600 mt-0.5 leading-relaxed">
              UrbanPulse supports Bright Data's{' '}
              <a href="https://docs.brightdata.com/ai/mcp-server/overview" target="_blank"
                 rel="noopener noreferrer" className="underline font-medium">
                Model Context Protocol (MCP) Server
              </a>{' '}
              — giving AI agents real-time access to web data via tools like{' '}
              <code className="text-[9px] px-1 py-0.5 bg-sky-100 rounded">search_engine</code>,{' '}
              <code className="text-[9px] px-1 py-0.5 bg-sky-100 rounded">scrape_as_markdown</code>, and{' '}
              <code className="text-[9px] px-1 py-0.5 bg-sky-100 rounded">web_data_google_maps_reviews</code>.
              Free tier includes 5,000 requests/month.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
