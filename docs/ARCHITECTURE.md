# Sabha AI: Architectural Decision Records & System Design

## 1. Product Identity & Philosophy

**Sabha (सभा)** represents an assembly of collective wisdom. While ordinary meeting tools merely transcribe speech, **Sabha AI** was engineered to turn conversations into verified commitments, reveal overlooked blind spots, and propose creative architectural solutions.

### Core Architectural Axioms
1. **Never Hallucinate Commitment**: If a speaker says *"Could someone check this?"*, the task is marked `unassigned`. We never invent an owner or deadline.
2. **Qualcomm-Only LLM Inference**: All generative synthesis and reasoning is powered exclusively by the **Qualcomm Cloud AI Playground**. No third-party LLMs are permitted.
3. **Deterministic First**: Calculations, counts, status tallies, date arithmetic, and permission checks are executed via Python and SQL—never spending expensive LLM tokens on arithmetic.
4. **Context Sieve Compression**: We preprocess transcripts to eliminate conversational filler and duplicate echoes while strictly preserving negation, commitment changes, and context windows.
5. **Verbatim Evidence Grounding**: Every generated task, decision, and risk retains a pointer to the source segment ID and an exact verbatim quote.

---

## 2. System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 SABHA AI CLIENT                                   |
|   React 18 + TypeScript + Vite + Tailwind CSS + LiveKit WebRTC SDK               |
+-----------------------------------------+-----------------------------------------+
                                          |
                +-------------------------+-------------------------+
                | HTTP REST (FastAPI)                               | WebSockets (/ws)
                v                                                   v
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                    |
|                                                                                   |
|  [Input Adapters]                                                                 |
|    - LiveKit WebRTC Token Service                                                 |
|    - Transcript Lab Parser (.txt, .md, .vtt)                                      |
|                                                                                   |
|  [Security & Multi-Tenancy]                                                       |
|    - RBAC: Participant, Host, Manager, Admin                                      |
|    - Tenant Isolation: Scoped by workspace_id                                     |
|    - Prompt Injection Sanitizer                                                   |
|                                                                                   |
|  [Core AI Pipeline: analyze_meeting()]                                            |
|    +---------------------------------------------------------------------------+  |
|    | 1. Context Sieve Preprocessor (Deduplication, Negation & Window Cues)     |  |
|    +-------------------------------------+-------------------------------------+  |
|                                          |                                        |
|    +-------------------------------------v-------------------------------------+  |
|    | 2. Token Budget Manager (Cost tracking, $2.50 cap, graceful degradation)  |  |
|    +-------------------------------------+-------------------------------------+  |
|                                          |                                        |
|    +-------------------------------------v-------------------------------------+  |
|    | 3. Qualcomm Model Router                                                  |  |
|    |    - Deterministic: Python/SQL ($0.00)                                    |  |
|    |    - Routine: Llama-3.1-8B ($0.05/M)                                      |  |
|    |    - Second Brain: Llama-3.3-70B ($0.35/M)                                |  |
|    |    - Flaw Detection: DeepSeek-R1 Distill ($0.50/M)                        |  |
|    |    - Creative: Qwen-QwQ-32B ($0.20/M)                                     |  |
|    +-------------------------------------+-------------------------------------+  |
|                                          |                                        |
|    +-------------------------------------v-------------------------------------+  |
|    | 4. Qualcomm Cloud AI Playground Client (Exclusive LLM Provider)           |  |
|    +-------------------------------------+-------------------------------------+  |
|                                          |                                        |
|    +-------------------------------------v-------------------------------------+  |
|    | 5. Evidence Validator (Verbatim quote match, negation checks, provenance) |  |
|    +---------------------------------------------------------------------------+  |
+-----------------------------------------+-----------------------------------------+
                                          |
         +--------------------------------+--------------------------------+
         |                                                                 |
         v                                                                 v
+----------------------------------+             +----------------------------------+
|      SQL DATABASE (SQLAlchemy)   |             |    LIVEKIT WEBRTC MEDIA CLOUD    |
| Users, Workspaces, Meetings,     |             | Audio/Video Rooms, SFU Tracks,   |
| Segments, Tasks, Intelligence,   |             | Real-time Participant State      |
| AI Usage & Audit Records         |             +----------------------------------+
+----------------------------------+
```

---

## 3. Core Innovation Deep-Dives

### Innovation A: Context Sieve (`context_sieve.py`)
Large transcripts often contain conversational filler (*"Can you hear me?"*, *"Yeah, cool"*), mic echoes, and conversational wandering. Sending all raw audio frames to an LLM is both slow and expensive.

The Context Sieve algorithm operates in two passes:
1. **Pass 1 (Intent Tagging & Deduplication)**:
   - Eliminates consecutive exact duplicates caused by audio stutter.
   - Discards pure conversational filler lacking intent tags.
   - Tags candidate sentences exhibiting key intents:
     - `TASK_CUES`: *"will"*, *"shall"*, *"handle"*, *"deploy"*, *"fix"*, etc.
     - `DECISION_CUES`: *"decide"*, *"agreed"*, *"approved"*, *"settled"*, etc.
     - `NEGATION_AND_CORRECTION_CUES`: *"not"*, *"cannot"*, *"actually"*, *"scratch that"*, *"disagree"*, etc.
     - `DATE_CUES`: *"by Friday"*, *"tomorrow"*, *"next week"*, etc.
     - `RISK_CUES`: *"blocker"*, *"danger"*, *"vulnerability"*, *"downtime"*, etc.
2. **Pass 2 (Context Window Expansion)**:
   - For every candidate sentence, the Sieve retains a sliding window (default: 1 segment before and 1 segment after).
   - This ensures pronouns, conversational flow, and speaker responses are never isolated.
   - Achieves 35%–60% token compression without losing conversational context.

### Innovation B: Qualcomm Model Router (`model_router.py`)
Rather than using a single model for every task, the Model Router assigns the lowest-cost suitable Qualcomm model:
- **Deterministic Code**: Exact quote matching, deadline arithmetic, task counts, and schema validation are handled in Python/SQL ($0.00 cost, 0 latency).
- **Llama-3.1-8B**: Fast, economical extraction of action items, decisions, and meeting summaries.
- **Llama-3.3-70B**: Nuanced multi-perspective Second Brain synthesis.
- **DeepSeek-R1 Distill (70B)**: Deep reasoning for flaw detection and contradiction analysis.
- **Qwen-QwQ-32B**: Divergent ideation for the Creative Solutions Engine.

### Innovation C: Evidence Validator (`evidence_validator.py`)
LLMs often hallucinate task owners or claim a deadline was established when it was merely a wish. The Evidence Validator applies strict safeguards:
- **Verbatim Quote Verification**: Verifies that quoted text actually appears in the source transcript segments.
- **Negation Checks**: If a quote includes *"actually I cannot proceed"*, an affirmative task claim is flagged with `ValidationStatus.CONFLICTING`.
- **Ownership Grounding**: If the assignee was not mentioned in the quote and was not the speaker, ownership is marked as `inferred` or unassigned.
- **Relative Deadlines**: Relative dates (*"by Friday"*) are flagged for meeting date resolution.

---

## 4. Multi-Tenancy & Security
- **Workspace Isolation**: All database queries enforce `workspace_id` scoping to prevent Insecure Direct Object References (IDOR).
- **Role-Based Access Control (RBAC)**:
  - *Participant*: View permitted meetings, manage assigned tasks, review AI findings.
  - *Host*: Create/manage meetings, invite participants, configure settings.
  - *Manager*: View team dashboard, inspect blocker matrix, reassign tasks.
  - *Admin*: Workspace settings, budget guardrails, integrations.
- **Prompt Injection Defense**: All transcripts and external web search snippets pass through `sanitize_untrusted_input()` to strip control delimiters and prompt overrides.
