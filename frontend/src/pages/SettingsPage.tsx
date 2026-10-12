import React, { useState, useEffect } from 'react';
import {
  Settings,
  Cpu,
  ShieldCheck,
  DollarSign,
  Layers,
  Key,
  Info,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [usage, setUsage] = useState<any>(null);
  const [meetingCap, setMeetingCap] = useState('2.50');
  const [savingCap, setSavingCap] = useState(false);

  useEffect(() => {
    api.getHealth().then(setHealth).catch(console.error);
    api.getUsageSummary().then(setUsage).catch(console.error);
  }, []);

  const handleUpdateCap = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingCap(true);
    try {
      const ws = api.getWorkspaceId();
      await fetch(`/api/v1/workspaces/${ws}/budget-limits`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('sabha_token')}`
        },
        body: JSON.stringify({ max_meeting_cost_usd: parseFloat(meetingCap) })
      });
      alert('Budget limit updated successfully.');
    } catch (e: any) {
      alert(e.message);
    } finally {
      setSavingCap(false);
    }
  };

  const isConfigured = health?.qualcomm_cloud_ai?.status === 'configured';

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16">
      <div className="pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-indigo-400" />
          <h1 className="text-2xl font-extrabold text-white">System Settings & Qualcomm Telemetry</h1>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Inspect Qualcomm Cloud AI Playground connectivity, model rate cards, and workspace budget limits.
        </p>
      </div>

      {/* Qualcomm Provider Status Card */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-950/80 border border-indigo-700/50 flex items-center justify-center">
              <Cpu className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Qualcomm Cloud AI Playground</h3>
              <p className="text-xs text-slate-400">Sole Authorized LLM Provider</p>
            </div>
          </div>

          <span className={`px-3 py-1 rounded-full text-xs font-semibold border flex items-center space-x-1.5 ${
            isConfigured
              ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300'
              : 'bg-amber-950/60 border-amber-500/50 text-amber-300'
          }`}>
            {isConfigured ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Live Endpoint Connected</span>
              </>
            ) : (
              <>
                <Info className="w-3.5 h-3.5" />
                <span>Demo Mode (Unconfigured in .env)</span>
              </>
            )}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono pt-2 border-t border-slate-800">
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[10px] uppercase">Base Endpoint:</span>
            <span className="text-indigo-300 truncate block mt-0.5">{health?.qualcomm_cloud_ai?.endpoint || 'https://api.cloudai.qualcomm.com/v1'}</span>
          </div>
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[10px] uppercase">Architectural Restriction:</span>
            <span className="text-emerald-400 block mt-0.5">Strict Qualcomm Only (Zero Third-Party LLMs)</span>
          </div>
        </div>

        {/* Model Rate Card Table */}
        <div className="space-y-2 pt-2">
          <span className="text-xs font-bold text-slate-300 block">Verified Qualcomm Cloud AI Model Registry:</span>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 text-[10px]">
                  <th className="pb-2 font-semibold">Model Name</th>
                  <th className="pb-2 font-semibold">Specialization</th>
                  <th className="pb-2 font-semibold">Input / 1M</th>
                  <th className="pb-2 font-semibold">Output / 1M</th>
                  <th className="pb-2 font-semibold">Context Window</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-[11px]">
                <tr>
                  <td className="py-2 text-indigo-300 font-bold">Llama-3.1-8B</td>
                  <td className="py-2 text-slate-300 font-sans">Routine Task & Decision Extraction</td>
                  <td className="py-2 text-slate-400">$0.05</td>
                  <td className="py-2 text-slate-400">$0.08</td>
                  <td className="py-2 text-teal-400">128k</td>
                </tr>
                <tr>
                  <td className="py-2 text-indigo-300 font-bold">Llama-3.3-70B</td>
                  <td className="py-2 text-slate-300 font-sans">Multi-Perspective Second Brain Synthesis</td>
                  <td className="py-2 text-slate-400">$0.35</td>
                  <td className="py-2 text-slate-400">$0.40</td>
                  <td className="py-2 text-teal-400">128k</td>
                </tr>
                <tr>
                  <td className="py-2 text-indigo-300 font-bold">DeepSeek-R1 Distill (70B)</td>
                  <td className="py-2 text-slate-300 font-sans">Flaw Detection & Contradiction Analysis</td>
                  <td className="py-2 text-slate-400">$0.50</td>
                  <td className="py-2 text-slate-400">$0.80</td>
                  <td className="py-2 text-teal-400">64k</td>
                </tr>
                <tr>
                  <td className="py-2 text-indigo-300 font-bold">Qwen-QwQ-32B</td>
                  <td className="py-2 text-slate-300 font-sans">Creative Problem Solving & Architectures</td>
                  <td className="py-2 text-slate-400">$0.20</td>
                  <td className="py-2 text-slate-400">$0.30</td>
                  <td className="py-2 text-teal-400">32k</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Budget Controls Card */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-teal-950/80 border border-teal-700/50 flex items-center justify-center">
            <DollarSign className="w-5 h-5 text-teal-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Token Budget Guardrails</h3>
            <p className="text-xs text-slate-400">Prevent runaway cloud inference expenses with automatic degradation</p>
          </div>
        </div>

        <form onSubmit={handleUpdateCap} className="flex flex-col sm:flex-row items-end gap-3 pt-2">
          <div className="w-full sm:w-64">
            <label className="text-xs text-slate-400 block mb-1">Max Cost Per Meeting (USD)</label>
            <input
              type="number"
              step="0.10"
              value={meetingCap}
              onChange={(e) => setMeetingCap(e.target.value)}
              className="w-full text-xs bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-500 font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={savingCap}
            className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 transition disabled:opacity-50"
          >
            {savingCap ? 'Saving...' : 'Update Cap'}
          </button>
        </form>

        {usage && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-800 text-xs font-mono">
            <div>
              <span className="text-slate-500 text-[10px] block">Total Processed Tokens:</span>
              <span className="text-white font-bold">{usage.total_tokens_processed}</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block">Total Spend (USD):</span>
              <span className="text-amber-300 font-bold">${usage.total_cost_usd?.toFixed(4)}</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block">Monthly Budget:</span>
              <span className="text-slate-300">${usage.monthly_budget_usd?.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block">Budget Utilized:</span>
              <span className="text-teal-400 font-bold">{usage.budget_usage_percent}%</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
