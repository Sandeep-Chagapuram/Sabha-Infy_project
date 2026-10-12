import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Video as VideoIcon,
  VideoOff,
  PhoneOff,
  Users,
  MessageSquare,
  Sparkles,
  Send,
  Brain
} from 'lucide-react';
import { api } from '../services/api';
import { TranscriptSegment } from '../types';

interface MeetingRoomPageProps {
  meetingId: string;
  onNavigate: (page: string, params?: any) => void;
}

export const MeetingRoomPage: React.FC<MeetingRoomPageProps> = ({ meetingId, onNavigate }) => {
  const [meeting, setMeeting] = useState<any>(null);
  const [micEnabled, setMicEnabled] = useState(true);
  const [camEnabled, setCamEnabled] = useState(false);
  const [segments, setSegments] = useState<TranscriptSegment[]>([]);
  const [currentSpeechInput, setCurrentSpeechInput] = useState('');
  const [simulatedSpeakers] = useState(['Priya Sharma (Host)', 'Vikram Desai', 'Rahul Verma', 'Neha Joshi']);
  const [selectedSpeaker, setSelectedSpeaker] = useState('Priya Sharma (Host)');
  const [ending, setEnding] = useState(false);
  const transcriptEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getMeetingDetail(meetingId).then(setMeeting).catch(console.error);
    api.getSegments(meetingId).then(setSegments).catch(console.error);
  }, [meetingId]);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [segments]);

  const handleSendSpeech = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentSpeechInput.trim()) return;

    try {
      const newSeg = await api.addSegment(meetingId, {
        sequence_number: segments.length,
        speaker_name: selectedSpeaker.split(' ')[0],
        text: currentSpeechInput.trim(),
        start_time: segments.length * 4.0
      });
      setSegments([...segments, newSeg]);
      setCurrentSpeechInput('');
    } catch (e: any) {
      alert(e.message);
    }
  };

  const handleEndAndAnalyze = async () => {
    setEnding(true);
    try {
      // 1. Mark meeting completed
      const ws = api.getWorkspaceId();
      await fetch(`/api/v1/workspaces/${ws}/meetings/${meetingId}/end`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('sabha_token')}` }
      });

      // 2. Trigger shared Qualcomm Analysis Pipeline
      await api.analyzeMeeting(meetingId, 'full', true);

      // 3. Navigate to Intelligence
      onNavigate('intelligence', { meetingId });
    } catch (e: any) {
      alert('Analysis error: ' + e.message);
    } finally {
      setEnding(false);
    }
  };

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col lg:flex-row gap-4 max-w-7xl mx-auto">
      {/* Video Conference Stage */}
      <div className="flex-1 flex flex-col bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        {/* Stage Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
            <div>
              <h2 className="text-sm font-bold text-white">{meeting?.title || 'Live Meeting'}</h2>
              <span className="text-[10px] text-slate-400 font-mono">LiveKit Room: {meeting?.livekit_room_name || 'Active'}</span>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Users className="w-4 h-4 text-indigo-400" />
            <span>4 Connected</span>
          </div>
        </div>

        {/* Video Tiles Grid */}
        <div className="flex-1 p-4 grid grid-cols-2 gap-3 overflow-y-auto">
          {simulatedSpeakers.map((speaker, idx) => {
            const isMe = idx === 0;
            return (
              <div
                key={speaker}
                className="relative rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col items-center justify-center p-6 overflow-hidden group shadow-inner"
              >
                {/* Simulated avatar tile */}
                <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-indigo-600 to-teal-500 flex items-center justify-center text-lg font-bold text-white shadow-lg">
                  {speaker[0]}
                </div>

                <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur-md px-2.5 py-1 rounded-md text-[11px] font-medium text-slate-200 border border-slate-800 flex items-center space-x-1.5">
                  <span>{speaker}</span>
                  {isMe && !micEnabled && <MicOff className="w-3 h-3 text-rose-400 ml-1" />}
                </div>

                {isMe && camEnabled && (
                  <div className="absolute inset-0 bg-indigo-950/20 backdrop-blur-none flex items-center justify-center text-[10px] text-indigo-300">
                    Video Stream Active (Local Track)
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Media Controls Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setMicEnabled(!micEnabled)}
              className={`p-3 rounded-xl transition ${
                micEnabled ? 'bg-slate-800 hover:bg-slate-700 text-white' : 'bg-rose-950/80 text-rose-400 border border-rose-800'
              }`}
            >
              {micEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
            </button>
            <button
              onClick={() => setCamEnabled(!camEnabled)}
              className={`p-3 rounded-xl transition ${
                camEnabled ? 'bg-indigo-600 text-white' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
              }`}
            >
              {camEnabled ? <VideoIcon className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
            </button>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleEndAndAnalyze}
              disabled={ending}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-teal-600 hover:from-indigo-500 hover:to-teal-500 shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
            >
              <Brain className="w-4 h-4" />
              <span>{ending ? 'Analyzing with Qualcomm AI...' : 'End & Analyze (Sabha Intelligence)'}</span>
            </button>
            <button
              onClick={() => onNavigate('meetings')}
              className="p-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white transition"
              title="Leave Room"
            >
              <PhoneOff className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Live Transcript Sidebar */}
      <div className="w-full lg:w-96 flex flex-col bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-2">
            <MessageSquare className="w-4 h-4 text-indigo-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">Live Transcript Feed</h3>
          </div>
          <span className="text-[10px] text-teal-400 font-mono px-2 py-0.5 rounded bg-teal-950/60 border border-teal-800/40">
            Real-Time Stream
          </span>
        </div>

        {/* Segments Stream */}
        <div className="flex-1 p-4 space-y-3 overflow-y-auto text-xs font-sans">
          {segments.length === 0 ? (
            <div className="p-6 text-center text-slate-500 italic">
              Speak or send a message below to generate live transcript segments.
            </div>
          ) : (
            segments.map((seg, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 space-y-1">
                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span className="font-bold text-indigo-300">{seg.speaker_name || 'Participant'}</span>
                  <span className="font-mono text-slate-500">
                    {seg.start_time !== undefined ? `[${seg.start_time.toFixed(1)}s]` : ''}
                  </span>
                </div>
                <p className="text-slate-200 leading-relaxed">{seg.text}</p>
              </div>
            ))
          )}
          <div ref={transcriptEndRef} />
        </div>

        {/* Live speech simulator input */}
        <form onSubmit={handleSendSpeech} className="p-3 border-t border-slate-800 bg-slate-950/80 space-y-2">
          <div className="flex items-center justify-between text-[10px] text-slate-400">
            <span>Simulate Speaker:</span>
            <select
              value={selectedSpeaker}
              onChange={(e) => setSelectedSpeaker(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded text-slate-200 px-1 py-0.5 text-[10px]"
            >
              {simulatedSpeakers.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={currentSpeechInput}
              onChange={(e) => setCurrentSpeechInput(e.target.value)}
              placeholder="Type speech utterance..."
              className="flex-1 text-xs bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
