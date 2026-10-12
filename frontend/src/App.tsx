import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { HomePage } from './pages/HomePage';
import { MeetingsPage } from './pages/MeetingsPage';
import { MeetingRoomPage } from './pages/MeetingRoomPage';
import { TranscriptLabPage } from './pages/TranscriptLabPage';
import { TasksPage } from './pages/TasksPage';
import { TeamDashboardPage } from './pages/TeamDashboardPage';
import { IntelligencePage } from './pages/IntelligencePage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>('home');
  const [pageParams, setPageParams] = useState<any>({});
  const [initialized, setInitialized] = useState<boolean>(false);

  useEffect(() => {
    // Automatically initialize authenticated demo session with default workspace
    api.initDemoSession()
      .then(() => setInitialized(true))
      .catch((e) => {
        console.error('Session init warning:', e);
        setInitialized(true);
      });
  }, []);

  const handleNavigate = (page: string, params: any = {}) => {
    setCurrentPage(page);
    setPageParams(params);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col font-sans">
      <Navbar onNavigate={handleNavigate} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentPage={currentPage} onNavigate={handleNavigate} />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {!initialized ? (
            <div className="h-64 flex items-center justify-center">
              <div className="w-8 h-8 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
            </div>
          ) : (
            <>
              {currentPage === 'home' && <HomePage onNavigate={handleNavigate} />}
              {currentPage === 'meetings' && <MeetingsPage onNavigate={handleNavigate} />}
              {currentPage === 'meeting_room' && (
                <MeetingRoomPage meetingId={pageParams.meetingId} onNavigate={handleNavigate} />
              )}
              {currentPage === 'lab' && <TranscriptLabPage onNavigate={handleNavigate} />}
              {currentPage === 'tasks' && <TasksPage />}
              {currentPage === 'team' && <TeamDashboardPage />}
              {currentPage === 'intelligence' && (
                <IntelligencePage
                  meetingId={pageParams.meetingId}
                  autoAnalyze={pageParams.autoAnalyze}
                  onNavigate={handleNavigate}
                />
              )}
              {currentPage === 'reports' && <ReportsPage />}
              {currentPage === 'settings' && <SettingsPage />}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
