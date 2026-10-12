import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { api } from '../services/api';

export const QualcommBadge: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch(() => setHealth({ qualcomm_cloud_ai: { status: 'unconfigured_offline' } }));
  }, []);

  const isConfigured = health?.qualcomm_cloud_ai?.status === 'configured';

  return (
    <div className="relative inline-block">
      <div 
        onClick={() => setShowTooltip(!showTooltip)}
        className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-medium border cursor-pointer transition-all ${
          isConfigured 
            ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300 hover:bg-emerald-900/60'
            : 'bg-amber-950/50 border-amber-500/40 text-amber-300 hover:bg-amber-900/50'
        }`}
      >
        <Cpu className="w-3.5 h-3.5 text-indigo-400" />
        <span className="font-semibold">Qualcomm Cloud AI</span>
        {isConfigured ? (
          <span className="flex items-center text-[10px] text-emerald-400 bg-emerald-900/80 px-1.5 py-0.5 rounded">
            <CheckCircle2 className="w-3 h-3 mr-1" /> Live Ready
          </span>
        ) : (
          <span className="flex items-center text-[10px] text-amber-400 bg-amber-900/80 px-1.5 py-0.5 rounded">
            <Info className="w-3 h-3 mr-1" /> Demo Mode
          </span>
        )}
      </div>

      {showTooltip && (
        <div className="absolute right-0 mt-2 w-80 p-3 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl z-50 text-xs">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="font-bold text-slate-200">Exclusive LLM Provider</span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-700">
              Qualcomm Cloud AI
            </span>
          </div>
          <div className="mt-2 space-y-1.5 text-slate-300">
            <p className="text-[11px] text-slate-400">
              Per strict architecture, all LLM intelligence is routed exclusively through the 
              <strong> Qualcomm Cloud AI Playground</strong>. No third-party LLMs are permitted.
            </p>
            <div className="pt-1.5 border-t border-slate-800 space-y-1 font-mono text-[10px]">
              <div className="flex justify-between">
                <span className="text-slate-400">Routine Extraction:</span>
                <span className="text-indigo-300">Llama-3.1-8B</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Second Brain (70B):</span>
                <span className="text-indigo-300">Llama-3.3-70B</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Flaw Detection:</span>
                <span className="text-indigo-300">DeepSeek-R1 Distill</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Creative Solutions:</span>
                <span className="text-indigo-300">Qwen-QwQ-32B</span>
              </div>
            </div>
            {!isConfigured && (
              <div className="mt-2 p-2 bg-amber-950/60 border border-amber-800/60 rounded text-amber-300 text-[10px]">
                <AlertCircle className="w-3.5 h-3.5 inline mr-1 text-amber-400" />
                QUALCOMM_API_KEY is not set in .env. Showing verified demo datasets without claiming live inference.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
