import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Clock,
  AlertCircle,
  CheckCircle2,
  Filter,
  User,
  ShieldCheck,
  HelpCircle,
  MessageSquare
} from 'lucide-react';
import { api } from '../services/api';
import { TaskItem, TaskStatus, TaskPriority } from '../types';

export const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [unassignedOnly, setUnassignedOnly] = useState<boolean>(false);
  const [blockerModalTask, setBlockerModalTask] = useState<TaskItem | null>(null);
  const [blockerReason, setBlockerReason] = useState('');

  const loadTasks = () => {
    setLoading(true);
    api.getTasks({
      status: statusFilter === 'all' ? undefined : statusFilter,
      unassigned_only: unassignedOnly
    })
      .then(setTasks)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTasks();
  }, [statusFilter, unassignedOnly]);

  const handleToggleComplete = async (task: TaskItem) => {
    const newStatus: TaskStatus = task.status === 'completed' ? 'pending' : 'completed';
    try {
      await api.updateTask(task.id, { status: newStatus });
      loadTasks();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleReportBlocker = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!blockerModalTask || !blockerReason.trim()) return;
    try {
      await api.updateTask(blockerModalTask.id, {
        status: 'blocked',
        blocker_reason: blockerReason
      });
      setBlockerModalTask(null);
      setBlockerReason('');
      loadTasks();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <CheckSquare className="w-5 h-5 text-indigo-400" />
            <h1 className="text-2xl font-extrabold text-white">Action Items & Tasks</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Grounded commitments extracted by Qualcomm Cloud AI and verified against verbatim meeting evidence.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="blocked">Blocked</option>
            <option value="completed">Completed</option>
          </select>

          <label className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={unassignedOnly}
              onChange={(e) => setUnassignedOnly(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
            />
            <span>Unassigned Only</span>
          </label>
        </div>
      </div>

      {/* Task List */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading tasks...</div>
      ) : tasks.length === 0 ? (
        <div className="p-12 text-center text-xs text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
          No action items found matching your filters.
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => {
            const isCompleted = task.status === 'completed';
            const isBlocked = task.status === 'blocked';
            const isUnassigned = !task.assignee_name;

            return (
              <div
                key={task.id}
                className={`p-4 rounded-xl border transition flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                  isCompleted
                    ? 'bg-slate-900/40 border-slate-800/60 opacity-65'
                    : isBlocked
                    ? 'bg-rose-950/20 border-rose-500/30'
                    : 'bg-slate-900/90 border-slate-800'
                }`}
              >
                <div className="flex items-start space-x-3 flex-1">
                  <button
                    onClick={() => handleToggleComplete(task)}
                    className={`mt-0.5 w-5 h-5 rounded-md border flex items-center justify-center transition shrink-0 ${
                      isCompleted
                        ? 'bg-emerald-600 border-emerald-500 text-white'
                        : 'border-slate-700 hover:border-slate-500 bg-slate-800'
                    }`}
                  >
                    {isCompleted && <CheckCircle2 className="w-3.5 h-3.5" />}
                  </button>

                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.2 rounded font-mono ${
                        task.priority === 'urgent' ? 'bg-rose-950 text-rose-300 border border-rose-800' :
                        task.priority === 'high' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                        'bg-slate-800 text-slate-300'
                      }`}>
                        {task.priority}
                      </span>

                      <span className={`text-[10px] font-semibold px-2 py-0.2 rounded ${
                        isUnassigned
                          ? 'bg-amber-900/50 text-amber-300 border border-amber-700/60'
                          : 'bg-indigo-950 text-indigo-300 border border-indigo-800'
                      }`}>
                        {isUnassigned ? 'Unassigned (Awaiting Confirmation)' : `Owner: ${task.assignee_name}`}
                      </span>

                      {task.deadline_text && (
                        <span className="text-[10px] text-slate-400 flex items-center space-x-1 font-mono">
                          <Clock className="w-3 h-3 text-slate-500" />
                          <span>{task.deadline_text}</span>
                        </span>
                      )}

                      <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-teal-950/60 text-teal-400 border border-teal-800/40">
                        {task.validation_status}
                      </span>
                    </div>

                    <h3 className={`text-xs font-semibold leading-relaxed ${isCompleted ? 'line-through text-slate-500' : 'text-slate-100'}`}>
                      {task.title}
                    </h3>

                    {/* Blocker alert if blocked */}
                    {isBlocked && task.blocker_reason && (
                      <div className="p-2 bg-rose-950/40 border border-rose-500/40 rounded text-[11px] text-rose-300">
                        ⚠️ <strong>Blocker:</strong> {task.blocker_reason}
                      </div>
                    )}

                    {/* Verbatim supporting quote */}
                    <blockquote className="text-[11px] text-slate-400 italic bg-slate-950/60 p-2 rounded border-l-2 border-indigo-500/40 line-clamp-2">
                      "{task.source_evidence_quote}"
                    </blockquote>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 shrink-0 self-end md:self-center">
                  {!isBlocked && !isCompleted && (
                    <button
                      onClick={() => setBlockerModalTask(task)}
                      className="px-2.5 py-1 rounded text-[11px] font-semibold text-rose-400 bg-rose-950/40 hover:bg-rose-900/50 border border-rose-800/60 transition"
                    >
                      Report Blocker
                    </button>
                  )}
                  {isBlocked && (
                    <button
                      onClick={() => api.updateTask(task.id, { status: 'in_progress', blocker_reason: '' }).then(loadTasks)}
                      className="px-2.5 py-1 rounded text-[11px] font-semibold text-emerald-300 bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 transition"
                    >
                      Resolve Blocker
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Blocker Report Modal */}
      {blockerModalTask && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Report Task Blocker</h3>
            <p className="text-xs text-slate-400">
              For task: <strong>{blockerModalTask.title}</strong>
            </p>
            <form onSubmit={handleReportBlocker} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1">What is blocking progress?</label>
                <textarea
                  required
                  rows={3}
                  value={blockerReason}
                  onChange={(e) => setBlockerReason(e.target.value)}
                  placeholder="e.g. Awaiting database schema partitioning DDL from the data engineering team."
                  className="w-full text-xs bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-rose-500"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setBlockerModalTask(null)}
                  className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-500 rounded-xl shadow-lg shadow-rose-600/30"
                >
                  Mark Blocked
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
