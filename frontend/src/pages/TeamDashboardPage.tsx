import React, { useState, useEffect } from 'react';
import {
  Users,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ShieldAlert,
  TrendingUp,
  BarChart3
} from 'lucide-react';
import { api } from '../services/api';

export const TeamDashboardPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTeamDashboard()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-xs text-slate-400">Loading team metrics...</div>;
  }

  const metrics = data?.task_metrics || {};
  const workload = data?.workload_by_member || {};
  const blockers = data?.active_blockers || [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      <div className="pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5 text-indigo-400" />
          <h1 className="text-2xl font-extrabold text-white">Manager & Team Dashboard</h1>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Deterministic SQL aggregations across team commitments, active blockers, and progress rates.
        </p>
      </div>

      {/* Top 4 Metric KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 block">Total Action Items</span>
          <div className="text-2xl font-extrabold text-white">{metrics.total || 0}</div>
          <span className="text-[10px] text-teal-400 font-mono">{metrics.completion_rate_percent || 0}% Completion Rate</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 block">Pending / In Progress</span>
          <div className="text-2xl font-extrabold text-indigo-400">{(metrics.pending || 0) + (metrics.in_progress || 0)}</div>
          <span className="text-[10px] text-slate-500 font-mono">Active commitments</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 block">Critical Blockers</span>
          <div className="text-2xl font-extrabold text-rose-400">{metrics.blocked || 0}</div>
          <span className="text-[10px] text-rose-400 font-mono">Requires managerial escalation</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 block">Unassigned Tasks</span>
          <div className="text-2xl font-extrabold text-amber-400">{metrics.unassigned || 0}</div>
          <span className="text-[10px] text-amber-400 font-mono">Awaiting owner designation</span>
        </div>
      </div>

      {/* Workload by Participant Table */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <BarChart3 className="w-4 h-4 text-indigo-400" />
            <span>Participant Workload Distribution</span>
          </h3>
          <span className="text-[10px] font-mono text-slate-500">Calculated via SQL grouping</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="pb-2 font-semibold">Team Member</th>
                <th className="pb-2 font-semibold">Pending</th>
                <th className="pb-2 font-semibold">In Progress</th>
                <th className="pb-2 font-semibold">Blocked</th>
                <th className="pb-2 font-semibold">Completed</th>
                <th className="pb-2 font-semibold">Total Assigned</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {Object.entries(workload).map(([name, counts]: [string, any]) => (
                <tr key={name} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-bold text-slate-200">{name}</td>
                  <td className="py-2.5 text-slate-400">{counts.pending}</td>
                  <td className="py-2.5 text-indigo-300">{counts.in_progress}</td>
                  <td className="py-2.5 text-rose-400">{counts.blocked > 0 ? `⚠️ ${counts.blocked}` : '0'}</td>
                  <td className="py-2.5 text-teal-400">{counts.completed}</td>
                  <td className="py-2.5 font-bold text-white">{counts.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Active Blockers Board */}
      {blockers.length > 0 && (
        <div className="p-5 rounded-2xl bg-rose-950/20 border border-rose-500/30 space-y-3">
          <h3 className="text-sm font-bold text-rose-300 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>Urgent Project Blockers Requiring Intervention</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {blockers.map((b: any) => (
              <div key={b.id} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-100">{b.title}</span>
                  <span className="text-[10px] text-indigo-300 font-mono">Owner: {b.assignee}</span>
                </div>
                <p className="text-[11px] text-rose-300 bg-rose-950/40 p-2 rounded border border-rose-900/50">
                  {b.blocker_reason}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
