export type MeetingInputSource = 'live_meeting' | 'pasted_transcript' | 'uploaded_transcript' | 'uploaded_audio';
export type MeetingStatus = 'scheduled' | 'in_progress' | 'completed' | 'analyzing' | 'analyzed' | 'failed';
export type TaskStatus = 'pending' | 'in_progress' | 'blocked' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type DeadlineConfidence = 'explicit' | 'inferred' | 'ambiguous' | 'unspecified';
export type ValidationStatus = 'explicitly_stated' | 'evidence_supported' | 'inferred' | 'conflicting' | 'unverified' | 'human_confirmed';

export interface Meeting {
  id: string;
  workspace_id: string;
  title: string;
  description?: string;
  input_source: MeetingInputSource;
  status: MeetingStatus;
  meeting_date: string;
  timezone: string;
  project_context?: string;
  livekit_room_name?: string;
  duration_seconds: number;
  raw_token_count: number;
  compressed_token_count: number;
  created_at: string;
  updated_at: string;
}

export interface TranscriptSegment {
  id: string;
  meeting_id: string;
  sequence_number: number;
  speaker_name?: string;
  text: string;
  start_time?: number;
  end_time?: number;
  status: 'provisional' | 'final';
  created_at: string;
}

export interface TaskItem {
  id: string;
  meeting_id: string;
  workspace_id: string;
  title: string;
  description?: string;
  assignee_id?: string;
  assignee_name?: string;
  is_ownership_confirmed: boolean;
  deadline?: string;
  deadline_text?: string;
  deadline_confidence: DeadlineConfidence;
  status: TaskStatus;
  priority: TaskPriority;
  priority_origin: string;
  blocker_reason?: string;
  source_segment_id?: string;
  source_evidence_quote: string;
  validation_status: ValidationStatus;
  created_at: string;
  updated_at: string;
}

export interface DecisionItem {
  id: string;
  meeting_id: string;
  workspace_id: string;
  title: string;
  description: string;
  status: 'confirmed' | 'proposed' | 'disputed';
  source_evidence_quote: string;
  source_segment_id?: string;
  validation_status: ValidationStatus;
  created_at: string;
}

export interface RiskItem {
  id: string;
  meeting_id: string;
  workspace_id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  potential_impact?: string;
  suggested_mitigation?: string;
  source_evidence_quote: string;
  source_segment_id?: string;
  validation_status: ValidationStatus;
  created_at: string;
}

export interface SecondBrainBelieveItem {
  item: string;
  type: string;
  evidence_quote: string;
  segment_id?: string;
}

export interface SecondBrainMissingItem {
  finding: string;
  concern_type: string;
  evidence_quote: string;
  reasoning: string;
  potential_impact: string;
  confidence: string;
  suggested_verification: string;
  recommended_mitigation?: string;
}

export interface SecondBrainInvestigateItem {
  recommendation: string;
  action_type: string;
  suggested_owner?: string;
  rationale: string;
  convertible_to_task: boolean;
}

export interface SecondBrainResponse {
  what_we_believe: SecondBrainBelieveItem[];
  what_we_might_be_missing: SecondBrainMissingItem[];
  what_to_investigate_next: SecondBrainInvestigateItem[];
  model_name: string;
  pipeline_version: string;
}

export interface CreativeApproach {
  title: string;
  explanation: string;
  expected_benefits: string[];
  limitations: string[];
  required_resources: string[];
  risks: string[];
  assumptions: string[];
  suggested_experiments: string[];
  evaluation_criteria_scores: Record<string, number>;
}

export interface CreativeSolutionsResponse {
  problem_statement: string;
  approaches: CreativeApproach[];
  model_name: string;
}

export interface ResearchSource {
  title: string;
  url: string;
  publication_date?: string;
  retrieval_date: string;
  excerpt: string;
}

export interface ResearchBriefResponse {
  question: string;
  summary: string;
  key_findings: string[];
  sources: ResearchSource[];
  uncertainty_and_limitations: string;
  suggested_follow_ups: string[];
  model_name: string;
}

export interface MeetingAnalysisResult {
  meeting_id: string;
  status: string;
  executive_summary: string;
  decisions: DecisionItem[];
  risks: RiskItem[];
  second_brain?: SecondBrainResponse;
  creative_solutions?: CreativeSolutionsResponse;
  research_briefs: ResearchBriefResponse[];
  tokens_raw: number;
  tokens_compressed: number;
  compression_ratio: number;
  estimated_cost_usd: number;
  model_used: string;
}

export interface DemoSample {
  id: string;
  title: string;
  category: string;
  description: string;
  transcript: string;
  meeting_date: string;
  timezone: string;
  participants: string[];
  project_context: string;
}

export interface TokenEstimate {
  word_count: number;
  char_count: number;
  estimated_tokens: number;
  estimated_cost_usd: number;
  segment_count: number;
}
