import React, { useState, useEffect } from 'react';
import { FileDown, FileText, Download, Calendar } from 'lucide-react';
import { api } from '../services/api';
import { Meeting } from '../types';

export const ReportsPage: React.FC = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState<string>('');
  const [format, setFormat] = useState<'markdown' | 'csv' | 'json'>('markdown');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    api.getMeetings().then((list) => {
      setMeetings(list);
      if (list.length > 0) setSelectedMeetingId(list[0].id);
    }).catch(console.error);
  }, []);

  const handleExport = async () => {
    if (!selectedMeetingId) return;
    setDownloading(true);
    try {
      const ws = api.getWorkspaceId();
      const token = localStorage.getItem('sabha_token');
      const res = await fetch(`/api/v1/workspaces/${ws}/meetings/${selectedMeetingId}/export?format=${format}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Export failed');

      if (format === 'json') {
        const json = await res.json();
        const blob = new Blob([JSON.stringify(json, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sabha_export_${selectedMeetingId.slice(0, 8)}.json`;
        a.click();
      } else {
        const text = await res.text();
        const blob = new Blob([text], { type: format === 'csv' ? 'text/csv' : 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sabha_export_${selectedMeetingId.slice(0, 8)}.${format === 'csv' ? 'csv' : 'md'}`;
        a.click();
      }
    } catch (e: any) {
      alert(e.message);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-16">
      <div className="pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <FileDown className="w-5 h-5 text-indigo-400" />
          <h1 className="text-2xl font-extrabold text-white">Insights & Export Reports</h1>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Export verified meeting intelligence, action items, and Second Brain reviews in Markdown, CSV, or JSON.
        </p>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-5">
        <div>
          <label className="text-xs font-semibold text-slate-300 block mb-1.5">Select Meeting Record</label>
          <select
            value={selectedMeetingId}
            onChange={(e) => setSelectedMeetingId(e.target.value)}
            className="w-full text-xs bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-white focus:outline-none focus:border-indigo-500"
          >
            {meetings.map((m) => (
              <option key={m.id} value={m.id}>
                {m.title} — {new Date(m.created_at).toLocaleDateString()} ({m.input_source})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-300 block mb-1.5">Export Format</label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'markdown', label: 'Markdown (.md)', desc: 'Executive brief formatted with headers & quotes' },
              { id: 'csv', label: 'Spreadsheet (.csv)', desc: 'Tabular action items, owners, and evidence' },
              { id: 'json', label: 'Structured JSON', desc: 'Full API payload for external integrations' },
            ].map((fmt) => (
              <button
                key={fmt.id}
                type="button"
                onClick={() => setFormat(fmt.id as any)}
                className={`p-3.5 rounded-xl border text-left transition ${
                  format === fmt.id
                    ? 'bg-indigo-600/15 border-indigo-500 text-white'
                    : 'bg-slate-800/60 border-slate-700/60 text-slate-400 hover:text-slate-200'
                }`}
              >
                <div className="font-bold text-xs">{fmt.label}</div>
                <div className="text-[10px] text-slate-500 mt-1">{fmt.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800 flex justify-end">
          <button
            onClick={handleExport}
            disabled={downloading || !selectedMeetingId}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span>{downloading ? 'Generating Report...' : `Export ${format.toUpperCase()}`}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
