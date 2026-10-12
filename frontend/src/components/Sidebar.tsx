import React from 'react';
import {
  Home,
  Video,
  FileCode2,
  CheckSquare,
  Users,
  Brain,
  FileDown,
  Settings,
  Sparkles
} from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'meetings', label: 'Meetings (Live)', icon: Video, badge: 'Mode A' },
    { id: 'lab', label: 'Transcript Lab', icon: FileCode2, badge: 'Mode B' },
    { id: 'tasks', label: 'My Tasks', icon: CheckSquare },
    { id: 'team', label: 'Team Workspace', icon: Users },
    { id: 'intelligence', label: 'Sabha Intelligence', icon: Brain, highlight: true },
    { id: 'reports', label: 'Insights & Reports', icon: FileDown },
    { id: 'settings', label: 'Settings & Budgets', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-[#0E1422] flex flex-col justify-between p-4 shrink-0">
      <div className="space-y-6">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-3">
            Core Collaboration
          </span>
          <nav className="mt-2 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold uppercase bg-slate-800 text-slate-300 border border-slate-700">
                      {item.badge}
                    </span>
                  )}
                  {item.highlight && (
                    <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Demo Mode Notice */}
        <div className="p-3 rounded-xl bg-gradient-to-b from-indigo-950/40 to-slate-900 border border-indigo-500/20 text-xs">
          <div className="flex items-center space-x-2 text-indigo-300 font-semibold mb-1">
            <Brain className="w-4 h-4 text-indigo-400" />
            <span>Dual-Input Ready</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Test live LiveKit audio/video or analyze transcripts in the Lab. Both modes share the exact same Qualcomm Cloud AI engine.
          </p>
        </div>
      </div>

      {/* User profile footer */}
      <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-teal-400 flex items-center justify-center font-bold text-xs text-white shadow">
            PS
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-200">Priya Sharma</div>
            <div className="text-[10px] text-slate-500">Lead Architect • Host</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
