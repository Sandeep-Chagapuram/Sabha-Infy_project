import React, { useState, useEffect } from 'react';
import {
  Brain,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Search,
  Check,
  X,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  HelpCircle,
  FileText,
  Cpu,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { MeetingAnalysisResult, Meeting } from '../types';

interface IntelligencePageProps {
  meetingId?: string;
  autoAnalyze?: boolean;
  onNavigate: (page: string, params?: any) => void;
}

export const IntelligencePage: React.FC<IntelligencePageProps> = ({ meetingId, autoAnalyze, onNavigate }) => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(meetingId || null);
  const [analysis, setAnalysis] = useState<MeetingAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'second_brain' | 'tasks_decisions' | 'creative' | 'research'>('second_brain');
  const [researchQuery, setResearchQuery] = useState('');
  const [researching, setResearching] = useState(false);

  useEffect(() => {
    api.getMeetings().then((list) => {
      setMeetings(list);
      if (!selectedMeetingId && list.length > 0) {
        setSelectedMeetingId(list[0].id);
      }
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedMeetingId) {
      setLoading(true);
      api.analyzeMeeting(selectedMeetingId, 'full', false)
        .then(setAnalysis)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [selectedMeetingId]);

  const handleConfirmDecision = async (decisionId: string, confirm: boolean) => {
    try {
      await api.confirmDecision(decisionId, confirm);
      if (selectedMeetingId) {
        const refreshed = await api.analyzeMeeting(selectedMeetingId, 'full', false);
        setAnalysis(refreshed);
      }
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleResearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!researchQuery.trim() || !selectedMeetingId) return;
    setResearching(true);
    try {
      const brief = await api.runResearch(selectedMeetingId, researchQuery);
      if (analysis) {
        setAnalysis({
          ...analysis,
          research_briefs: [brief, ...(analysis.research_briefs || [])]
        });
      }
      setResearchQuery('');
    } catch (e: any) {
      alert('Research error: ' + e.message);
    } finally {
      setResearching(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header & Meeting Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Intelligence Engine
            </span>
            <h1 className="text-2xl font-extrabold text-white">Sabha Intelligence</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Evidence-grounded Second Brain Review, Creative Solutions, and decision tracking powered by Qualcomm Cloud AI.
          </p>
        </div>

        {/* Meeting Dropdown Selector */}
        <div className="flex items-center space-x-2">
          <label className="text-xs text-slate-400">Meeting:</label>
          <select
            value={selectedMeetingId || ''}
            onChange={(e) => setSelectedMeetingId(e.target.value)}
            className="text-xs bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-indigo-500"
          >
            {meetings.map((m) => (
              <option key={m.id} value={m.id}>
                {m.title} ({new Date(m.created_at).toLocaleDateString()})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="p-16 flex flex-col items-center justify-center space-y-3 bg-slate-900/40 rounded-2xl border border-slate-800">
          <div className="w-8 h-8 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
          <span className="text-xs text-slate-400 font-mono">Running Context Sieve & Qualcomm Model Router...</span>
        </div>
      ) : analysis ? (
        <div className="space-y-6">
          {/* Executive Summary & Token Compression Telemetry Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-[#111827] to-slate-900 border border-slate-800 space-y-4 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center space-x-1.5">
                <Brain className="w-4 h-4" />
                <span>Executive Summary</span>
              </span>
              <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
                <span className="px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800">
                  Model: {analysis.model_used}
                </span>
                <span className="px-2 py-0.5 rounded bg-teal-950/80 text-teal-300 border border-teal-800">
                  Compression: {analysis.compression_ratio}% ({analysis.tokens_compressed} / {analysis.tokens_raw} tokens)
                </span>
                <span className="px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800">
                  Est. Cost: ${analysis.estimated_cost_usd.toFixed(5)}
                </span>
              </div>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed font-sans">
              {analysis.executive_summary}
            </p>
          </div>

          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-800 space-x-4">
            <button
              onClick={() => setActiveTab('second_brain')}
              className={`pb-3 text-xs font-bold transition flex items-center space-x-1.5 ${
                activeTab === 'second_brain'
                  ? 'border-b-2 border-indigo-500 text-indigo-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Brain className="w-4 h-4" />
              <span>Second Brain Review</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-950 text-indigo-300">Flagship</span>
            </button>
            <button
              onClick={() => setActiveTab('tasks_decisions')}
              className={`pb-3 text-xs font-bold transition flex items-center space-x-1.5 ${
                activeTab === 'tasks_decisions'
                  ? 'border-b-2 border-indigo-500 text-indigo-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Decisions & Action Items</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                {(analysis.decisions?.length || 0) + (analysis.risks?.length || 0)}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('creative')}
              className={`pb-3 text-xs font-bold transition flex items-center space-x-1.5 ${
                activeTab === 'creative'
                  ? 'border-b-2 border-indigo-500 text-indigo-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Lightbulb className="w-4 h-4" />
              <span>Creative Solutions Engine</span>
            </button>
            <button
              onClick={() => setActiveTab('research')}
              className={`pb-3 text-xs font-bold transition flex items-center space-x-1.5 ${
                activeTab === 'research'
                  ? 'border-b-2 border-indigo-500 text-indigo-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Research Assistant</span>
            </button>
          </div>

          {/* TAB 1: SECOND BRAIN REVIEW */}
          {activeTab === 'second_brain' && (
            <div className="space-y-6">
              {analysis.second_brain ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Perspective A: What We Believe */}
                  <div className="space-y-3">
                    <div className="p-3 rounded-xl bg-teal-950/40 border border-teal-500/30 flex items-center space-x-2">
                      <ShieldCheck className="w-4 h-4 text-teal-400 shrink-0" />
                      <div>
                        <h3 className="font-bold text-xs text-teal-300">A. What We Believe</h3>
                        <p className="text-[10px] text-teal-500">Confirmed decisions & commitments</p>
                      </div>
                    </div>

                    <div className="space-y-2.5">
                      {analysis.second_brain.what_we_believe.map((item, idx) => (
                        <div key={idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[9px] uppercase px-1.5 py-0.5 rounded bg-teal-950 text-teal-300 border border-teal-800">
                              {item.type}
                            </span>
                          </div>
                          <p className="font-medium text-slate-200 leading-snug">{item.item}</p>
                          <blockquote className="p-2 bg-slate-950/80 rounded border-l-2 border-teal-500/60 text-[11px] text-slate-400 italic">
                            "{item.evidence_quote}"
                          </blockquote>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Perspective B: What We Might Be Missing */}
                  <div className="space-y-3">
                    <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 flex items-center space-x-2">
                      <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                      <div>
                        <h3 className="font-bold text-xs text-rose-300">B. What We Might Be Missing</h3>
                        <p className="text-[10px] text-rose-500">Blind spots, risks & contradictions</p>
                      </div>
                    </div>

                    <div className="space-y-2.5">
                      {analysis.second_brain.what_we_might_be_missing.map((item, idx) => (
                        <div key={idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[9px] uppercase px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                              {item.concern_type}
                            </span>
                            <span className="text-[10px] text-slate-400">Confidence: {item.confidence}</span>
                          </div>
                          <p className="font-medium text-slate-200 leading-snug">{item.finding}</p>
                          <p className="text-[11px] text-slate-400">
                            <strong>Reasoning:</strong> {item.reasoning}
                          </p>
                          <blockquote className="p-2 bg-slate-950/80 rounded border-l-2 border-rose-500/60 text-[11px] text-slate-400 italic">
                            "{item.evidence_quote}"
                          </blockquote>
                          {item.suggested_verification && (
                            <div className="pt-1 text-[11px] text-indigo-300">
                              🔍 <strong>Verification:</strong> {item.suggested_verification}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Perspective C: What to Investigate Next */}
                  <div className="space-y-3">
                    <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30 flex items-center space-x-2">
                      <HelpCircle className="w-4 h-4 text-indigo-400 shrink-0" />
                      <div>
                        <h3 className="font-bold text-xs text-indigo-300">C. What to Investigate Next</h3>
                        <p className="text-[10px] text-indigo-500">Experiments & follow-up research</p>
                      </div>
                    </div>

                    <div className="space-y-2.5">
                      {analysis.second_brain.what_to_investigate_next.map((item, idx) => (
                        <div key={idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[9px] uppercase px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                              {item.action_type}
                            </span>
                            {item.suggested_owner && (
                              <span className="text-[10px] text-slate-300 font-medium">Owner: {item.suggested_owner}</span>
                            )}
                          </div>
                          <p className="font-medium text-slate-200 leading-snug">{item.recommendation}</p>
                          <p className="text-[11px] text-slate-400">
                            <strong>Rationale:</strong> {item.rationale}
                          </p>
                          <div className="pt-2 flex justify-end">
                            <button
                              onClick={() => onNavigate('tasks')}
                              className="text-[10px] px-2.5 py-1 rounded bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700 transition"
                            >
                              + Convert to Task
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400 text-xs bg-slate-900/40 rounded-xl border border-slate-800">
                  Second Brain Review was not generated for this analysis run.
                </div>
              )}
            </div>
          )}

          {/* TAB 2: DECISIONS & RISKS */}
          {activeTab === 'tasks_decisions' && (
            <div className="space-y-6">
              {/* Decisions section */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-teal-400" />
                  <span>Decisions Grounded in Conversation</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {analysis.decisions.map((dec) => (
                    <div key={dec.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2.5">
                      <div className="flex items-center justify-between">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          dec.status === 'confirmed' ? 'bg-teal-950 text-teal-300 border border-teal-800' : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}>
                          {dec.status}
                        </span>
                        <div className="flex items-center space-x-1">
                          <button
                            onClick={() => handleConfirmDecision(dec.id, true)}
                            title="Confirm Decision"
                            className="p-1 hover:bg-teal-950 rounded text-slate-400 hover:text-teal-300 transition"
                          >
                            <Check className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleConfirmDecision(dec.id, false)}
                            title="Dispute Decision"
                            className="p-1 hover:bg-rose-950 rounded text-slate-400 hover:text-rose-300 transition"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                      <h4 className="font-bold text-slate-100">{dec.title}</h4>
                      <p className="text-slate-300">{dec.description}</p>
                      <blockquote className="p-2 bg-slate-950 rounded border-l-2 border-teal-500/70 text-[11px] text-slate-400 italic">
                        "{dec.source_evidence_quote}"
                      </blockquote>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risks section */}
              <div className="space-y-3 pt-4 border-t border-slate-800">
                <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>Flagged Risks & Potential Failure Modes</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {analysis.risks.map((risk) => (
                    <div key={risk.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2">
                      <div className="flex items-center justify-between">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          risk.severity === 'critical' ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}>
                          Severity: {risk.severity}
                        </span>
                      </div>
                      <h4 className="font-bold text-slate-100">{risk.title}</h4>
                      <p className="text-slate-300">{risk.description}</p>
                      {risk.suggested_mitigation && (
                        <p className="text-[11px] text-indigo-300">
                          🛡️ <strong>Mitigation:</strong> {risk.suggested_mitigation}
                        </p>
                      )}
                      <blockquote className="p-2 bg-slate-950 rounded border-l-2 border-amber-500/70 text-[11px] text-slate-400 italic">
                        "{risk.source_evidence_quote}"
                      </blockquote>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: CREATIVE SOLUTIONS ENGINE */}
          {activeTab === 'creative' && (
            <div className="space-y-4">
              {analysis.creative_solutions ? (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/20 text-xs">
                    <span className="font-bold text-amber-300 uppercase tracking-wider text-[10px] block mb-1">
                      Identified Bottleneck
                    </span>
                    <p className="text-slate-200 font-medium">
                      {analysis.creative_solutions.problem_statement}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {analysis.creative_solutions.approaches.map((app, idx) => (
                      <div key={idx} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3 flex flex-col justify-between">
                        <div className="space-y-2">
                          <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                            Approach #{idx + 1}
                          </span>
                          <h4 className="font-bold text-sm text-slate-100">{app.title}</h4>
                          <p className="text-xs text-slate-300 leading-relaxed">{app.explanation}</p>

                          <div className="pt-2 space-y-1.5">
                            <span className="text-[10px] font-semibold text-teal-400 block">Expected Benefits:</span>
                            <ul className="list-disc list-inside text-[11px] text-slate-400 space-y-0.5">
                              {app.expected_benefits.map((b, i) => <li key={i}>{b}</li>)}
                            </ul>
                          </div>

                          <div className="pt-2 space-y-1.5">
                            <span className="text-[10px] font-semibold text-rose-400 block">Trade-offs & Risks:</span>
                            <ul className="list-disc list-inside text-[11px] text-slate-400 space-y-0.5">
                              {app.risks.map((r, i) => <li key={i}>{r}</li>)}
                            </ul>
                          </div>
                        </div>

                        <div className="pt-3 border-t border-slate-800 text-[10px] text-slate-500">
                          Routed model: Qualcomm Qwen-QwQ-32B
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400 text-xs bg-slate-900/40 rounded-xl border border-slate-800">
                  No creative solution approaches generated for this run.
                </div>
              )}
            </div>
          )}

          {/* TAB 4: RESEARCH ASSISTANT */}
          {activeTab === 'research' && (
            <div className="space-y-4">
              {/* Query form */}
              <form onSubmit={handleResearchSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={researchQuery}
                  onChange={(e) => setResearchQuery(e.target.value)}
                  placeholder="Enter a technical or market question to research and ground with citations..."
                  className="flex-1 text-xs bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="submit"
                  disabled={researching || !researchQuery.trim()}
                  className="px-5 py-2.5 rounded-xl font-bold text-xs text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/30 transition disabled:opacity-50 flex items-center space-x-1.5"
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>{researching ? 'Synthesizing...' : 'Run Research'}</span>
                </button>
              </form>

              {/* Research briefs */}
              <div className="space-y-4">
                {analysis.research_briefs && analysis.research_briefs.length > 0 ? (
                  analysis.research_briefs.map((brief, idx) => (
                    <div key={idx} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                        <h4 className="font-bold text-slate-100 text-sm">{brief.question}</h4>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300">
                          {brief.model_name}
                        </span>
                      </div>
                      <p className="text-slate-300 leading-relaxed">{brief.summary}</p>

                      {/* Verifiable Sources */}
                      <div className="space-y-2 pt-2">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          Verifiable Sourced Citations:
                        </span>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {brief.sources.map((src, i) => (
                            <a
                              key={i}
                              href={src.url}
                              target="_blank"
                              rel="noreferrer"
                              className="p-2.5 rounded-lg bg-slate-950 hover:bg-slate-800/80 border border-slate-800 transition block text-[11px]"
                            >
                              <div className="font-semibold text-indigo-300 truncate">{src.title}</div>
                              <div className="text-slate-500 text-[10px] truncate">{src.url}</div>
                              <p className="text-slate-400 mt-1 line-clamp-2 italic">"{src.excerpt}"</p>
                            </a>
                          ))}
                        </div>
                      </div>

                      {brief.uncertainty_and_limitations && (
                        <div className="p-2 bg-amber-950/30 border border-amber-800/40 rounded text-[11px] text-amber-300">
                          <strong>Limitations & Uncertainty:</strong> {brief.uncertainty_and_limitations}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center text-slate-400 text-xs bg-slate-900/40 rounded-xl border border-slate-800">
                    No research briefs requested yet. Submit a question above to retrieve live citations synthesized with Qualcomm Cloud AI.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="p-12 text-center text-slate-400 text-xs bg-slate-900/40 rounded-2xl border border-slate-800">
          No meeting selected or available. Please load a sample or paste a transcript in the Lab.
        </div>
      )}
    </div>
  );
};
