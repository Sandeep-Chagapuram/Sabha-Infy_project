import React from 'react';
import { QualcommBadge } from './QualcommBadge';
import { Sparkles, Video, FileText } from 'lucide-react';

interface NavbarProps {
  onNavigate: (page: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate }) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-[#0B0F19]/90 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      {/* Brand & Logo */}
      <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate('home')}>
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-teal-400 p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <div className="w-full h-full bg-[#0B0F19] rounded-[10px] flex items-center justify-center">
            {/* Sabha emblem: interconnected assembly motif */}
            <svg className="w-5 h-5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3.2" />
              <path d="M12 2v3.5" />
              <path d="M12 18.5V22" />
              <path d="M2 12h3.5" />
              <path d="M18.5 12H22" />
              <path d="M4.93 4.93l2.47 2.47" />
              <path d="M16.6 16.6l2.47 2.47" />
              <path d="M4.93 19.07l2.47-2.47" />
              <path d="M16.6 7.4l2.47-2.47" />
            </svg>
          </div>
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
              Sabha AI
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              v1.0
            </span>
          </div>
          <p className="text-[11px] text-slate-400 hidden sm:block">
            Every conversation. A smarter decision.
          </p>
        </div>
      </div>

      {/* Dual Input Mode Quick Actions */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => onNavigate('meetings')}
          className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-800/80 hover:bg-slate-700 border border-slate-700/80 transition"
        >
          <Video className="w-3.5 h-3.5 text-indigo-400" />
          <span>Live Meeting</span>
        </button>
        <button
          onClick={() => onNavigate('lab')}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 shadow-md shadow-indigo-600/25 transition"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Transcript Lab</span>
          <span className="hidden sm:inline-block ml-1 text-[9px] bg-indigo-900/60 text-indigo-200 px-1 py-0.2 rounded border border-indigo-400/30">
            Dual-Mode
          </span>
        </button>

        <div className="h-4 w-px bg-slate-800 mx-1 hidden sm:block" />

        {/* Qualcomm Cloud AI Status Badge */}
        <QualcommBadge />
      </div>
    </header>
  );
};
