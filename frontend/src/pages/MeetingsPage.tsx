import React, { useState, useEffect } from 'react';
import { Video, Plus, Calendar, Clock, FileText, ArrowRight, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { Meeting } from '../types';

interface MeetingsPageProps {
  onNavigate: (page: string, params?: any) => void;
}

export const MeetingsPage: React.FC<MeetingsPageProps> = ({ onNavigate }) => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newContext, setNewContext] = useState('');

  const loadMeetings = () => {
    setLoading(true);
    api.getMeetings()
      .then(setMeetings)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadMeetings();
  }, []);

  const handleCreateMeeting = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      const created = await api.createMeeting({
        title: newTitle,
        input_source: 'live_meeting',
        project_context: newContext
      });
      setShowCreateModal(false);
      setNewTitle('');
      setNewContext('');
      onNavigate('meeting_room', { meetingId: created.id });
    } catch (e: any) {
      alert(e.message || 'Failed to create meeting');
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Mode A
            </span>
            <h1 className="text-2xl font-extrabold text-white">Live Meetings</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time audio, video, and live transcript streaming powered by LiveKit WebRTC infrastructure.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/30 transition self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>New Live Meeting</span>
        </button>
      </div>

      {/* Meeting list */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading meetings...</div>
      ) : meetings.length === 0 ? (
        <div className="p-12 text-center text-xs text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
          No meetings found. Start a new live meeting or analyze a transcript in the Lab.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {meetings.map((m) => (
            <div
              key={m.id}
              className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded font-mono ${
                    m.input_source === 'live_meeting' ? 'bg-indigo-950 text-indigo-300 border border-indigo-800' : 'bg-teal-950 text-teal-300 border border-teal-800'
                  }`}>
                    {m.input_source.replace('_', ' ')}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded uppercase font-semibold ${
                    m.status === 'analyzed' ? 'bg-emerald-950 text-emerald-300' : m.status === 'in_progress' ? 'bg-indigo-950 text-indigo-300 animate-pulse' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {m.status}
                  </span>
                </div>

                <h3 className="font-bold text-sm text-slate-100">{m.title}</h3>
                {m.project_context && (
                  <p className="text-xs text-slate-400 line-clamp-2">{m.project_context}</p>
                )}

                <div className="flex items-center space-x-3 text-[11px] text-slate-500 pt-1">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{new Date(m.created_at).toLocaleDateString()}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{m.timezone}</span>
                  </span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end space-x-2">
                {m.input_source === 'live_meeting' && m.status !== 'analyzed' && (
                  <button
                    onClick={() => onNavigate('meeting_room', { meetingId: m.id })}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 transition"
                  >
                    <Video className="w-3.5 h-3.5" />
                    <span>Join Room</span>
                  </button>
                )}
                <button
                  onClick={() => onNavigate('intelligence', { meetingId: m.id })}
                  className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 transition"
                >
                  <FileText className="w-3.5 h-3.5 text-indigo-400" />
                  <span>View Intelligence</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Create Live Meeting</h3>
            <form onSubmit={handleCreateMeeting} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Meeting Name</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Core Architecture Review"
                  className="w-full text-xs bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Project Context</label>
                <textarea
                  value={newContext}
                  onChange={(e) => setNewContext(e.target.value)}
                  placeholder="Optional background or objectives"
                  rows={3}
                  className="w-full text-xs bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg shadow-indigo-600/30"
                >
                  Launch Room
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
