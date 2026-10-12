# Sabha AI: API Reference & Endpoint Specification

Base URL: `http://localhost:8000/api/v1`  
OpenAPI / Swagger UI: `http://localhost:8000/docs`

---

## 1. Authentication & Workspaces

### `POST /auth/register`
Creates a new user and provisions a default workspace.
- **Request Body**:
  ```json
  {
    "email": "user@company.com",
    "password": "SecurePassword123!",
    "full_name": "Priya Sharma",
    "workspace_name": "Engineering Council"
  }
  ```
- **Response `200`**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user_id": "uuid-...",
    "email": "user@company.com",
    "full_name": "Priya Sharma",
    "default_workspace_id": "uuid-..."
  }
  ```

### `POST /auth/login`
Authenticates an existing user.
- **Request Body**:
  ```json
  {
    "email": "user@company.com",
    "password": "SecurePassword123!"
  }
  ```

### `GET /auth/me`
Retrieves the profile of the authenticated user.
- **Headers**: `Authorization: Bearer <token>`

---

## 2. Meetings & LiveKit (Mode A)

### `POST /workspaces/{ws_id}/meetings`
Creates a scheduled or live meeting.
- **Request Body**:
  ```json
  {
    "title": "Sprint Planning Sync",
    "description": "Scope lock and blocker review",
    "input_source": "live_meeting",
    "timezone": "Asia/Kolkata",
    "project_context": "v1.0 release planning"
  }
  ```

### `POST /workspaces/{ws_id}/meetings/{meeting_id}/livekit-token`
Issues a scoped, short-lived JWT token to join the WebRTC LiveKit media room.
- **Response `200`**:
  ```json
  {
    "token": "eyJhbGciOi...",
    "room_name": "sabha-3f8d91a2",
    "participant_identity": "uuid-...",
    "participant_name": "Priya Sharma",
    "server_url": "https://sabha.livekit.cloud"
  }
  ```

### `POST /workspaces/{ws_id}/meetings/{meeting_id}/end`
Marks the live meeting completed and prepares transcript for analysis.

---

## 3. Transcript Lab (Mode B)

### `POST /workspaces/{ws_id}/transcript-lab/estimate?content={text}`
Calculates character count, word count, estimated tokens, and cost before analysis.
- **Response `200`**:
  ```json
  {
    "word_count": 142,
    "char_count": 980,
    "estimated_tokens": 258,
    "estimated_cost_usd": 0.000013,
    "segment_count": 7
  }
  ```

### `POST /workspaces/{ws_id}/transcript-lab/paste`
Parses raw text, creates a meeting record, and extracts segments.
- **Request Body**:
  ```json
  {
    "title": "Payment Webhook Review",
    "content": "[00:01:15] Priya: We must finish load testing by Friday.\n[00:01:22] Vikram: I will handle the load testing.",
    "meeting_date": "2026-10-15T10:00:00Z",
    "timezone": "Asia/Kolkata",
    "project_context": "Core Payment Microservice"
  }
  ```

### `POST /workspaces/{ws_id}/transcript-lab/upload`
Uploads `.txt`, `.md`, or `.vtt` file via `multipart/form-data`.

---

## 4. Sabha Intelligence Pipeline

### `POST /workspaces/{ws_id}/meetings/{meeting_id}/analyze`
Triggers the shared analysis pipeline: Context Sieve $\rightarrow$ Qualcomm Model Router $\rightarrow$ Evidence Validator.
- **Request Body**:
  ```json
  {
    "depth": "full",
    "force_recompute": false
  }
  ```
- **Response `200`**:
  ```json
  {
    "meeting_id": "uuid-...",
    "status": "analyzed",
    "executive_summary": "The team reviewed the v1.0 Product Launch...",
    "decisions": [ ... ],
    "risks": [ ... ],
    "second_brain": {
      "what_we_believe": [ ... ],
      "what_we_might_be_missing": [ ... ],
      "what_to_investigate_next": [ ... ]
    },
    "creative_solutions": {
      "problem_statement": "...",
      "approaches": [ ... ]
    },
    "tokens_raw": 1250,
    "tokens_compressed": 740,
    "compression_ratio": 40.8,
    "estimated_cost_usd": 0.00037,
    "model_used": "Llama-3.1-8B"
  }
  ```

### `POST /workspaces/{ws_id}/meetings/{meeting_id}/research?question={query}`
Executes external web retrieval with verifiable citations and Qualcomm LLM synthesis.

---

## 5. Tasks & Personal Dashboard

### `GET /workspaces/{ws_id}/tasks`
Lists action items with optional query filters:
- `?status=pending|in_progress|blocked|completed`
- `?unassigned_only=true`
- `?meeting_id={id}`

### `PATCH /workspaces/{ws_id}/tasks/{task_id}`
Updates task status, assignee, deadline, or reports a blocker.
- **Request Body**:
  ```json
  {
    "status": "blocked",
    "blocker_reason": "Waiting on Singapore team partitioning DDL"
  }
  ```

---

## 6. Manager Dashboard & Analytics

### `GET /workspaces/{ws_id}/dashboard/team`
Returns deterministic SQL metrics:
- Task metrics (`total`, `pending`, `blocked`, `completed`, `completion_rate_percent`)
- Workload by participant
- Active blockers board
- Decision & risk counts

---

## 7. Reports & Exports

### `GET /workspaces/{ws_id}/meetings/{meeting_id}/export?format=markdown|csv|json`
Downloads meeting intelligence report in the requested format with evidence provenance.
