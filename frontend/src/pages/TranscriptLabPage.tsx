import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  Sparkles,
  Calculator,
  ArrowRight,
  Clock,
  Globe,
  Layers,
  AlertCircle,
  FileCode,
  Check
} from 'lucide-react';
import { api } from '../services/api';
import { TokenEstimate, DemoSample } from '../types';

interface TranscriptLabPageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const TranscriptLabPage: React.FC<TranscriptLabPageProps> = ({ onNavigate }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [meetingDate, setMeetingDate] = useState(new Date().toISOString().split('T')[0]);
  const [timezone, setTimezone] = useState('Asia/Kolkata');
  const [projectContext, setProjectContext] = useState('');
  const [analysisDepth, setAnalysisDepth] = useState('full');
  const [estimate, setEstimate] = useState<TokenEstimate | null>(null);
  const [samples, setSamples] = useState<DemoSample[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    api.getDemoSamples().then(setSamples).catch(console.error);
  }, []);

  // Update token estimate whenever content changes
  useEffect(() => {
    if (!content.trim()) {
      setEstimate(null);
      return;
    }
    const timer = setTimeout(() => {
      api.estimateTranscript(content)
        .then(setEstimate)
        .catch(console.error);
    }, 400);
    return () => clearTimeout(timer);
  }, [content]);

  const handleSelectSample = (sample: DemoSample) => {
    setTitle(sample.title);
    setContent(sample.transcript);
    setMeetingDate(sample.meeting_date.split('T')[0]);
    setTimezone(sample.timezone);
    setProjectContext(sample.project_context);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['txt', 'md', 'vtt'].includes(ext || '')) {
      setUploadError('Unsupported file type. Please upload a .txt, .md, or .vtt file.');
      return;
    }

    try {
      const text = await file.text();
      setContent(text);
      if (!title) {
        setTitle(file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' '));
      }
    } catch (err: any) {
      setUploadError('Failed to read transcript file: ' + err.message);
    }
  };

  const handleAnalyze = async () => {
    if (!content.trim()) {
      alert('Please enter or upload a transcript first.');
      return;
    }

    setAnalyzing(true);
    try {
      // 1. Submit to Transcript Lab
      const pasteRes = await api.pasteTranscript({
        title: title || 'Transcript Lab Session',
        content,
        meeting_date: meetingDate,
        timezone,
        project_context: projectContext
      });

      // 2. Trigger shared Analysis Pipeline
      await api.analyzeMeeting(pasteRes.meeting_id, analysisDepth, true);

      // 3. Navigate to Intelligence Dashboard
      onNavigate('intelligence', { meetingId: pasteRes.meeting_id });
    } catch (err: any) {
      alert('Analysis error: ' + (err.message || 'Unknown error'));
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Mode B
            </span>
            <h1 className="text-2xl font-extrabold text-white">Transcript Lab</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Paste meeting notes or import .txt, .md, and WebVTT files. Sabha AI processes transcripts with the exact same Qualcomm Cloud AI pipeline as live meetings.
          </p>
        </div>

        {/* Sample Loaders */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Load sample:</span>
          {samples.map((s) => (
            <button
              key={s.id}
              onClick={() => handleSelectSample(s)}
              className="text-[11px] px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              {s.id === 'sample_a' ? 'Launch' : s.id === 'sample_b' ? 'At Risk' : 'Creative'}
            </button>
          ))}
        </div>
      </div>

      {uploadError && (
        <div className="p-3 bg-rose-950/50 border border-rose-500/40 rounded-xl text-xs text-rose-300 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Configuration Metadata Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div>
          <label className="text-[11px] font-semibold text-slate-400 block mb-1">Meeting Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Sprint 24 Planning & Scope Lock"
            className="w-full text-xs bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="text-[11px] font-semibold text-slate-400 block mb-1">Meeting Date (for relative deadlines)</label>
          <input
            type="date"
            value={meetingDate}
            onChange={(e) => setMeetingDate(e.target.value)}
            className="w-full text-xs bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="text-[11px] font-semibold text-slate-400 block mb-1">Timezone</label>
          <select
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            className="w-full text-xs bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
            <option value="America/New_York">America/New_York (EST)</option>
            <option value="America/Los_Angeles">America/Los_Angeles (PST)</option>
            <option value="Europe/London">Europe/London (GMT)</option>
            <option value="UTC">UTC</option>
          </select>
        </div>

        <div>
          <label className="text-[11px] font-semibold text-slate-400 block mb-1">Analysis Depth</label>
          <select
            value={analysisDepth}
            onChange={(e) => setAnalysisDepth(e.target.value)}
            className="w-full text-xs bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="full">Full Intelligence (Second Brain + Creative)</option>
            <option value="essential">Essential (Tasks, Decisions, Summary)</option>
            <option value="full_research">Full + Live Research Synthesis</option>
          </select>
        </div>
      </div>

      {/* Editor & Dropzone Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs">
          <label className="font-semibold text-slate-300 flex items-center space-x-2">
            <FileCode className="w-4 h-4 text-indigo-400" />
            <span>Transcript Content</span>
            <span className="text-slate-500 font-normal">
              (Supports [00:01:23] Name: text, Name: text, or WebVTT cues)
            </span>
          </label>

          {/* File Upload Button */}
          <label className="cursor-pointer flex items-center space-x-1 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition">
            <Upload className="w-3.5 h-3.5 text-indigo-400" />
            <span>Import .txt / .md / .vtt</span>
            <input type="file" accept=".txt,.md,.vtt" onChange={handleFileUpload} className="hidden" />
          </label>
        </div>

        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={16}
          placeholder="Paste meeting transcript here...&#10;&#10;Example:&#10;[00:01:15] Priya: We need to finish the API integration by Friday.&#10;[00:01:22] Rahul: I will handle the authentication changes.&#10;[00:01:40] Vikram: Let's officially decide to use PostgreSQL."
          className="w-full bg-[#0D1322] border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 leading-relaxed"
        />
      </div>

      {/* Telemetry and Action Footer */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-slate-900/80 rounded-xl border border-slate-800">
        {/* Token Counter & Estimates */}
        <div className="flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center space-x-1.5 text-slate-400">
            <Calculator className="w-3.5 h-3.5 text-indigo-400" />
            <span>Words: <strong className="text-slate-200">{estimate?.word_count || 0}</strong></span>
          </div>
          <div className="flex items-center space-x-1.5 text-slate-400">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Segments: <strong className="text-slate-200">{estimate?.segment_count || 0}</strong></span>
          </div>
          <div className="flex items-center space-x-1.5 text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            <span>Estimated Tokens: <strong className="text-teal-300">{estimate?.estimated_tokens || 0}</strong></span>
          </div>
          <div className="flex items-center space-x-1.5 text-slate-400">
            <span>Est. Cost: <strong className="text-amber-300 font-mono">${(estimate?.estimated_cost_usd || 0).toFixed(5)}</strong></span>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={handleAnalyze}
          disabled={analyzing || !content.trim()}
          className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl font-bold text-xs text-white bg-gradient-to-r from-indigo-600 to-teal-600 hover:from-indigo-500 hover:to-teal-500 shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
        >
          {analyzing ? (
            <>
              <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              <span>Context Sieve Processing & Qualcomm Reasoning...</span>
            </>
          ) : (
            <>
              <span>Analyze Transcript</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
