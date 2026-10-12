# Sabha AI (सभा AI)

> **"Every conversation. A smarter decision."**

Sabha AI is an enterprise meeting collaboration and decision intelligence platform. Rooted in the Sanskrit word **Sabha** (*an assembly, gathering, or council of wisdom*), it combines real-time WebRTC collaboration, evidence-grounded action item extraction, multi-perspective **Second Brain Reviews**, creative problem solving, and cost-efficient AI orchestration.

All LLM intelligence in Sabha AI is powered **exclusively by Qualcomm Cloud AI Playground**.

---

## 🌟 Key Product Innovations

### 1. Dual-Input Mode
- **Mode A: Live Meeting**: Real-time WebRTC audio/video meetings powered by LiveKit with participant tiles, mic/camera controls, live transcript streaming, and one-click post-meeting analysis.
- **Mode B: Transcript Lab**: A dedicated environment where users paste meeting transcripts or import `.txt`, `.md`, and `.vtt` files. Includes live token estimation, meeting date/timezone context, and one-click demonstration scenarios.
- **Unified Backend Pipeline**: Both modes call the exact same `analyze_meeting()` service.

### 2. Context Sieve Preprocessing (`context_sieve.py`)
- Eliminates audio stutter, exact echoes, and conversational filler before sending data to the LLM.
- Strictly preserves negations (*"cannot"*, *"won't"*), commitment changes (*"I will do it"* $\rightarrow$ *"Actually, I cannot"*), disagreements, dates, and conversational context windows.
- Achieves **35%–60% token compression** while guaranteeing evidence integrity.

### 3. Qualcomm-Only Model Router (`model_router.py`)
- **Exclusive LLM Provider**: Qualcomm Cloud AI Playground. No third-party LLMs (OpenAI, Claude, Gemini, Groq) are permitted.
- **Intelligent Task Routing**:
  - *Deterministic Operations*: Python/SQL (zero LLM token cost).
  - *Routine Extraction & Decisions*: **Qualcomm Llama-3.1-8B** ($0.05 / 1M tokens).
  - *Second Brain Multi-Perspective Synthesis*: **Qualcomm Llama-3.3-70B** ($0.35 / 1M tokens).
  - *Flaw Detection & Contradiction Analysis*: **Qualcomm DeepSeek-R1 Distill (70B)** ($0.50 / 1M tokens).
  - *Creative Solutions Engine*: **Qualcomm Qwen-QwQ-32B** ($0.20 / 1M tokens).
- **Honest Diagnostics**: If `QUALCOMM_API_KEY` is not configured, the platform clearly enters Demo Mode with pre-verified datasets, never fabricating live inference or falling back to another provider.

### 4. Evidence Validator (`evidence_validator.py`)
- Verifies that quoted evidence actually appears in the source transcript.
- Guards against hallucinated assignees: tasks are marked unassigned unless explicitly committed to.
- Flags relative deadlines lacking date context.
- Categorizes claims: `explicitly_stated`, `evidence_supported`, `inferred`, `conflicting`, `unverified`.

### 5. Flagship Second Brain Review
- **A. What We Believe**: Confirmed decisions, team assumptions, commitments, and constraints.
- **B. What We Might Be Missing**: Contradictions, unsupported assumptions, missing dependencies, and potential risks.
- **C. What to Investigate Next**: Small experiments, research spikes, and follow-up actions with one-click conversion to tasks.

### 6. Creative Solutions Engine
- Identifies the core bottleneck discussed in a meeting and formulates 3 distinct architectural approaches with benefit/risk trade-off matrices.

### 7. Research Assistant
- Retrieves verifiable web sources (via Tavily or search providers) and synthesizes research briefs strictly using Qualcomm Cloud AI with verifiable citations.

---

## 🛠️ Technology Architecture

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons | Responsive SaaS web application & Live meeting room |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, WebSockets | Application APIs, real-time events, and AI pipelines |
| **Real-time Infrastructure**| LiveKit WebRTC SDK | Video conferencing, participant tokens, audio streams |
| **LLM Inference** | **Qualcomm Cloud AI Playground** | Sole LLM inference provider for all intelligence features |
| **Database** | PostgreSQL / SQLite, SQLAlchemy ORM, Alembic | Multi-tenant workspace data, tasks, and audit logs |
| **Testing** | pytest, pytest-asyncio | Automated unit, regression, and security test suite |
| **Containerization** | Docker, Docker Compose | Production multi-container deployment |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js v18+ and npm
- (Optional) Docker & Docker Compose

### 1. Clone & Setup Backend
```bash
# Clone the repository
cd Sabha-Infy_project

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env
```

### 2. Configure Environment (`.env`)
Edit `.env` to configure your credentials:
```ini
# Core
ENVIRONMENT=development
SECRET_KEY=sabha-enterprise-secret-key-12345

# Qualcomm Cloud AI Playground (Exclusive Provider)
QUALCOMM_API_KEY=your_qualcomm_api_key_here
QUALCOMM_ENDPOINT=https://api.cloudai.qualcomm.com/v1

# LiveKit (Mode A)
LIVEKIT_URL=https://your-project.livekit.cloud
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```
> *Note: If `QUALCOMM_API_KEY` is omitted, Sabha AI automatically operates in honest Demo Mode with pre-verified datasets. It will never crash or fabricate live inference.*

### 3. Run Backend Server
```bash
source venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Setup & Run Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at: **http://localhost:3000**

---

## 🐳 Docker Deployment

To launch the complete Sabha AI stack (Backend + Frontend) via Docker Compose:
```bash
docker-compose up --build
```
- Web Application: `http://localhost:3000`
- API & Swagger: `http://localhost:8000/docs`

---

## 🧪 Automated Test Suite

Sabha AI includes 20 comprehensive unit and integration tests covering:
- **Context Sieve**: Stutter deduplication, negation preservation, token compression.
- **Evidence Validator**: Exact quote matching, hallucination detection, negation conflicts.
- **Qualcomm Model Router**: Verification that only Qualcomm models are registered, routing logic, and honest authentication error handling.
- **Token Budget**: Meeting budget caps, graceful degradation.
- **Transcript Parsers**: WebVTT, timestamps, unattributed plain text.
- **Security**: Prompt injection sanitization.

Run tests:
```bash
source venv/bin/activate
cd backend
PYTHONPATH=. pytest -v
```

---

## 📁 Repository Structure

```
Sabha-Infy_project/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint & WebSockets
│   │   ├── core/                    # Config, Security, DB Engine
│   │   ├── models/                  # SQLAlchemy models (User, Meeting, Task, Intelligence)
│   │   ├── schemas/                 # Pydantic schemas
│   │   ├── api/                     # REST API routes (Auth, Meetings, Lab, Tasks, Intelligence)
│   │   ├── ai/
│   │   │   ├── provider.py          # Exclusive Qualcomm Cloud AI Client
│   │   │   ├── model_registry.py    # Qualcomm model rate cards & specs
│   │   │   ├── model_router.py      # Task routing between Qualcomm models
│   │   │   ├── context_sieve.py     # Core innovation: Context Sieve
│   │   │   ├── evidence_validator.py# Evidence grounding & hallucination defense
│   │   │   ├── token_budget.py      # Budget limits ($2.50 cap) & graceful degradation
│   │   │   ├── pipeline.py          # Shared analysis pipeline
│   │   │   ├── demo_samples.py      # Demo transcripts & verified datasets
│   │   │   └── research_service.py  # Web search & Qualcomm LLM synthesis
│   │   └── meetings/
│   │       ├── livekit_service.py   # LiveKit WebRTC token generator
│   │       └── transcript_parser.py # Multi-format parser (.txt, .md, .vtt)
│   ├── tests/                       # Automated test suite (pytest)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/              # Navbar, Sidebar, QualcommBadge
│   │   ├── pages/                   # Home, Meetings, MeetingRoom, TranscriptLab, Tasks, Team, Intelligence, Reports, Settings
│   │   ├── services/api.ts          # Backend API client
│   │   ├── types/index.ts           # TypeScript interfaces
│   │   └── App.tsx                  # Main router & layout
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docker/                          # Dockerfiles for backend and frontend
├── docs/                            # In-depth architectural & API documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🤝 License & Credits
Built for the Hackathon with enterprise rigor. 
Sabha AI: *Every conversation. A smarter decision.*
