import {
  Meeting,
  TranscriptSegment,
  TaskItem,
  MeetingAnalysisResult,
  DemoSample,
  TokenEstimate,
  ResearchBriefResponse
} from '../types';

const API_BASE = '/api/v1';

class ApiService {
  private token: string | null = null;
  private currentWorkspaceId: string | null = null;

  constructor() {
    this.token = localStorage.getItem('sabha_token');
    this.currentWorkspaceId = localStorage.getItem('sabha_workspace_id');
  }

  setAuth(token: string, workspaceId: string) {
    this.token = token;
    this.currentWorkspaceId = workspaceId;
    localStorage.setItem('sabha_token', token);
    localStorage.setItem('sabha_workspace_id', workspaceId);
  }

  getWorkspaceId(): string {
    return this.currentWorkspaceId || 'default-ws';
  }

  private headers(isJson: boolean = true): HeadersInit {
    const h: Record<string, string> = {};
    if (isJson) {
      h['Content-Type'] = 'application/json';
    }
    if (this.token) {
      h['Authorization'] = `Bearer ${this.token}`;
    }
    return h;
  }

  // Health
  async getHealth() {
    const res = await fetch('/api/health');
    return res.json();
  }

  // Auth & Init Default Session if needed
  async initDemoSession() {
    try {
      const regRes = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'demo@sabha.ai',
          password: 'Password123!',
          full_name: 'Priya Sharma (Lead Architect)',
          workspace_name: 'Sabha Engineering Workspace'
        })
      });
      if (regRes.ok) {
        const data = await regRes.json();
        this.setAuth(data.access_token, data.default_workspace_id);
        return data;
      }
    } catch (e) {
      // User might already exist, login instead
    }

    const loginRes = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'demo@sabha.ai',
        password: 'Password123!'
      })
    });
    if (loginRes.ok) {
      const data = await loginRes.json();
      this.setAuth(data.access_token, data.default_workspace_id);
      return data;
    }
    throw new Error('Could not initialize session.');
  }

  // Meetings
  async getMeetings(): Promise<Meeting[]> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/meetings`, {
      headers: this.headers()
    });
    if (!res.ok) throw new Error('Failed to load meetings');
    return res.json();
  }

  async createMeeting(data: { title: string; description?: string; input_source: string; project_context?: string }): Promise<Meeting> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/meetings`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create meeting');
    return res.json();
  }

  async getMeetingDetail(meetingId: string): Promise<any> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/meetings/${meetingId}`, {
      headers: this.headers()
    });
    if (!res.ok) throw new Error('Failed to load meeting details');
    return res.json();
  }

  async getLiveKitToken(meetingId: string) {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/meetings/${meetingId}/livekit-token`, {
      method: 'POST',
      headers: this.headers()
    });
    if (!res.ok) throw new Error('Failed to generate LiveKit token');
    return res.json();
  }

  // Transcripts & Segments
  async getSegments(meetingId: string): Promise<TranscriptSegment[]> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/meetings/${meetingId}/segments`, {
      headers: this.headers()
    });
    if (!res.ok) throw new Error('Failed to load transcript segments');
    return res.json();
  }

  async addSegment(meetingId: string, data: { sequence_number: number; text: string; speaker_name?: string; start_time?: number }) {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/meetings/${meetingId}/segments`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(data)
    });
    return res.json();
  }

  // Transcript Lab
  async estimateTranscript(content: string): Promise<TokenEstimate> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/transcript-lab/estimate?content=${encodeURIComponent(content)}`, {
      method: 'POST',
      headers: this.headers()
    });
    if (!res.ok) throw new Error('Estimation failed');
    return res.json();
  }

  async pasteTranscript(data: {
    title: string;
    content: string;
    meeting_date?: string;
    timezone?: string;
    project_context?: string;
  }) {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/transcript-lab/paste`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to paste transcript');
    return res.json();
  }

  async uploadTranscript(formData: FormData) {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/transcript-lab/upload`, {
      method: 'POST',
      headers: this.headers(false),
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload transcript file');
    return res.json();
  }

  // Intelligence & Demos
  async getDemoSamples(): Promise<DemoSample[]> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/demo-samples`, {
      headers: this.headers()
    });
    if (!res.ok) throw new Error('Failed to load demo samples');
    return res.json();
  }

  async loadDemoSample(sampleId: string) {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/demo-samples/${sampleId}/load`, {
      method: 'POST',
      headers: this.headers()
    });
    if (!res.ok) throw new Error('Failed to load demo sample into workspace');
    return res.json();
  }

  async analyzeMeeting(meetingId: string, depth: string = 'full', force: boolean = false): Promise<MeetingAnalysisResult> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/meetings/${meetingId}/analyze`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ depth, force_recompute: force })
    });
    if (!res.ok) throw new Error('Analysis pipeline execution failed');
    return res.json();
  }

  async runResearch(meetingId: string, question: string): Promise<ResearchBriefResponse> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/meetings/${meetingId}/research?question=${encodeURIComponent(question)}`, {
      method: 'POST',
      headers: this.headers()
    });
    if (!res.ok) throw new Error('Research execution failed');
    return res.json();
  }

  async confirmDecision(decisionId: string, confirm: boolean) {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/decisions/${decisionId}/confirm?confirm=${confirm}`, {
      method: 'POST',
      headers: this.headers()
    });
    return res.json();
  }

  // Tasks
  async getTasks(params?: { status?: string; unassigned_only?: boolean; meeting_id?: string }): Promise<TaskItem[]> {
    const ws = this.getWorkspaceId();
    let url = `${API_BASE}/workspaces/${ws}/tasks`;
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append('status', params.status);
    if (params?.unassigned_only) searchParams.append('unassigned_only', 'true');
    if (params?.meeting_id) searchParams.append('meeting_id', params.meeting_id);
    if (searchParams.toString()) url += `?${searchParams.toString()}`;

    const res = await fetch(url, { headers: this.headers() });
    if (!res.ok) throw new Error('Failed to load tasks');
    return res.json();
  }

  async updateTask(taskId: string, data: Partial<TaskItem>): Promise<TaskItem> {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/tasks/${taskId}`, {
      method: 'PATCH',
      headers: this.headers(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update task');
    return res.json();
  }

  // Dashboards
  async getPersonalDashboard() {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/dashboard/personal`, {
      headers: this.headers()
    });
    return res.json();
  }

  async getTeamDashboard() {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/dashboard/team`, {
      headers: this.headers()
    });
    return res.json();
  }

  async getUsageSummary() {
    const ws = this.getWorkspaceId();
    const res = await fetch(`${API_BASE}/workspaces/${ws}/usage`, {
      headers: this.headers()
    });
    return res.json();
  }
}

export const api = new ApiService();
