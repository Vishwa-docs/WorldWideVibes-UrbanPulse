import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { askAgent } from '../../services/api';
import type { PersonaType, ScenarioType, Property, AgentResponse } from '../../types';

interface AgentChatProps {
  persona: PersonaType;
  scenario: ScenarioType;
  onPropertySelect?: (property: Property) => void;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  response?: AgentResponse;
}

export default function AgentChat({ persona, scenario, onPropertySelect }: AgentChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [lensOpen, setLensOpen] = useState<Record<string, boolean>>({});
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const resp = await askAgent(query, persona, scenario);
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: resp.answer,
        response: resp,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleLens = (key: string) => {
    setLensOpen((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white"
      >
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4" />
          <span className="text-sm font-medium">AI Copilot</span>
          {messages.length > 0 && (
            <span className="bg-white/20 text-[10px] px-1.5 py-0.5 rounded-full">
              {messages.length}
            </span>
          )}
        </div>
        {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
      </button>

      {expanded && (
        <div className="flex flex-col" style={{ height: '320px' }}>
          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 text-xs pt-8">
                <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
                Ask me about properties, scores, or investment opportunities
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                {msg.role === 'assistant' && (
                  <Bot className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                )}
                <div
                  className={`rounded-lg px-3 py-2 text-sm max-w-[85%] ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-50 text-gray-800 border border-gray-100'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {/* Recommended properties */}
                  {msg.response?.recommended_properties && msg.response.recommended_properties.length > 0 && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs font-medium text-indigo-600">Recommended:</p>
                      {msg.response.recommended_properties.map((p) => (
                        <button
                          key={p.id}
                          onClick={() => onPropertySelect?.(p)}
                          className="block w-full text-left text-xs bg-white rounded px-2 py-1 border border-indigo-100 hover:bg-indigo-50 transition-colors"
                        >
                          {p.address}
                          {p.score && (
                            <span className="ml-1 text-indigo-600 font-medium">
                              ({p.score.overall_score.toFixed(1)})
                            </span>
                          )}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Lens outputs */}
                  {msg.response?.lens_outputs && (
                    <div className="mt-2 space-y-1">
                      {Object.entries(msg.response.lens_outputs).map(([key, value]) => {
                        if (!value) return null;
                        const label = key === 'equity' ? '⚖️ Equity' : key === 'risk' ? '⚠️ Risk' : '💼 BizCoach';
                        const isOpen = lensOpen[`${i}-${key}`];
                        return (
                          <div key={key} className="border border-gray-200 rounded">
                            <button
                              onClick={() => toggleLens(`${i}-${key}`)}
                              className="w-full text-left px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50 flex items-center justify-between"
                            >
                              {label}
                              {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                            </button>
                            {isOpen && (
                              <div className="px-2 pb-2 text-xs text-gray-600 whitespace-pre-wrap">
                                {value}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
                {msg.role === 'user' && (
                  <User className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-2">
                <Bot className="w-5 h-5 text-indigo-600 flex-shrink-0" />
                <div className="bg-gray-50 rounded-lg px-3 py-2 border border-gray-100">
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-gray-100 p-2 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about properties..."
              className="flex-1 text-sm px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
