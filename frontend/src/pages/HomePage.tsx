import React, { useState, useEffect } from 'react';
import { Video, FileText, Sparkles, ArrowRight, CheckCircle2, ShieldAlert, Lightbulb, ExternalLink } from 'lucide-react';
import { api } from '../services/api';
import { DemoSample } from '../types';

interface HomePageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  const [samples, setSamples] = useState<DemoSample[]>([]);
  const [loadingSample, setLoadingSample] = useState<string | null>(null);

  useEffect(() => {
    api.getDemoSamples().then(setSamples).catch(console.error);
  }, []);

  const handleLoadSample = async (sampleId: string) => {
    setLoadingSample(sampleId);
    try {
      const res = await api.loadDemoSample(sampleId);
      onNavigate('intelligence', { meetingId: res.meeting_id, autoAnalyze: true });
    } catch (e: any) {
      alert(e.message || 'Failed to load demo sample');
    } finally {
      setLoadingSample(null);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950/70 via-slate-900 to-[#111827] border border-indigo-500/20 p-8 shadow-2xl">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Dual-Input Architecture • Qualcomm Cloud AI Exclusive</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Every conversation. <br />
            <span className="bg-gradient-to-r from-indigo-400 to-teal-300 bg-clip-text text-transparent">
              A smarter decision.
            </span>
          </h1>
          <p className="text-sm md:text-base text-slate-300 leading-relaxed">
            Sabha AI transforms team gatherings into verified commitments, uncovers hidden blind spots with 
            the <strong>Second Brain Review</strong>, and proposes breakthrough architectures—powered exclusively by 
            Qualcomm Cloud AI Playground and Context Sieve token compression.
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <button
              onClick={() => onNavigate('lab')}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold text-xs md:text-sm text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/30 transition"
            >
              <FileText className="w-4 h-4" />
              <span>Launch Transcript Lab (Mode B)</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
            <button
              onClick={() => onNavigate('meetings')}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold text-xs md:text-sm text-slate-200 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 transition"
            >
              <Video className="w-4 h-4 text-indigo-400" />
              <span>Start Live Meeting (Mode A)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Demo Workspace Scenarios */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-100">Hackathon Demonstration Scenarios</h2>
            <p className="text-xs text-slate-400">
              One-click preloaded meeting transcripts demonstrating Sabha AI's evidence validation and intelligence features.
            </p>
          </div>
          <span className="text-[11px] font-mono uppercase bg-amber-950/60 text-amber-300 border border-amber-600/30 px-2 py-0.5 rounded">
            Fictional Demo Datasets
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {samples.map((sample) => {
            const isA = sample.id === 'sample_a';
            const isB = sample.id === 'sample_b';
            const Icon = isA ? CheckCircle2 : isB ? ShieldAlert : Lightbulb;
            const accentColor = isA ? 'text-teal-400' : isB ? 'text-rose-400' : 'text-amber-400';
            const borderColor = isA ? 'hover:border-teal-500/50' : isB ? 'hover:border-rose-500/50' : 'hover:border-amber-500/50';

            return (
              <div
                key={sample.id}
                className={`p-5 rounded-xl bg-slate-900/80 border border-slate-800/90 transition-all flex flex-col justify-between ${borderColor} group`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {sample.category}
                    </span>
                    <Icon className={`w-4 h-4 ${accentColor}`} />
                  </div>
                  <h3 className="font-bold text-sm text-slate-100 group-hover:text-indigo-300 transition">
                    {sample.title}
                  </h3>
                  <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                    {sample.description}
                  </p>
                  <div className="pt-2 flex flex-wrap gap-1.5">
                    {sample.participants.map((p) => (
                      <span key={p} className="text-[10px] px-2 py-0.5 bg-slate-800/60 text-slate-300 rounded font-mono">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-800 flex justify-end">
                  <button
                    disabled={loadingSample === sample.id}
                    onClick={() => handleLoadSample(sample.id)}
                    className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-indigo-300 bg-indigo-950/60 hover:bg-indigo-900 border border-indigo-700/50 transition disabled:opacity-50"
                  >
                    <span>{loadingSample === sample.id ? 'Loading...' : 'Load & Analyze'}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Feature Pillar Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4">
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <div className="text-indigo-400 font-bold text-sm mb-1">Context Sieve Preprocessing</div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Eliminates audio stutter and chatter while strictly preserving negations, commitments, and surrounding context.
          </p>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <div className="text-teal-400 font-bold text-sm mb-1">Qualcomm-Only Model Router</div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Routes routine tasks to Llama-3.1-8B, Second Brain to Llama-3.3-70B, and creative tasks to Qwen-QwQ-32B.
          </p>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <div className="text-amber-400 font-bold text-sm mb-1">Evidence Validator</div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Guarantees every task and decision quotes verbatim evidence from transcript segments. Never invents an owner.
          </p>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <div className="text-purple-400 font-bold text-sm mb-1">Second Brain Review</div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Synthesizes What We Believe, What We Might Be Missing, and What to Investigate Next.
          </p>
        </div>
      </div>
    </div>
  );
};
