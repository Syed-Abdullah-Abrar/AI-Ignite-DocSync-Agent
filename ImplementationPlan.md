# Implementation Plan: DocSync (Healthcare Coordination Agent)

> Last Updated: 2026-04-16

## Overview

DocSync is an intermediate healthcare coordination agent that bridges patients on a web chat interface to doctors via ABDM UHI APIs. It uses LangGraph to orchestrate symptom intake, history retrieval, diagnostic reasoning (MiniMax m2.7), FHIR report generation, and appointment booking.

## Architecture Decisions

- **Orchestration:** LangGraph (Python) for stateful, cyclic clinical reasoning.
- **Reasoning Engine:** MiniMax m2.7 via OpenAI-compatible API for clinical diagnosis.
- **Database:** SQLite (via aiosqlite) for development; PostgreSQL (via asyncpg) for production.
- **Messaging:** Web chat interface (single-page HTML/CSS/JS served by FastAPI).
- **Standards:** FHIR R4 (Fast Healthcare Interoperability Resources) for all clinical reports.
- **Discovery:** ABDM Unified Health Interface (UHI) for doctor search and booking (mock for prototype).
- **Dashboard:** React Three Fiber for 3D visualization (separate Next.js app).
- **Observability:** Langfuse (configured, not yet active).

## Current Project Structure

```
DocSync/
├── src/
│   ├── __init__.py              # Package marker
│   ├── config.py                 # Environment configuration (dataclasses)
│   │
│   ├── agents/                  # LangGraph nodes
│   │   ├── __init__.py          # Exports all node functions
│   │   ├── steward.py           # Red flag detection (emergency triage)
│   │   ├── emergency.py         # Emergency routing & messaging
│   │   ├── symptom.py           # NLP symptom extraction (8 categories)
│   │   ├── history.py           # Patient medical history retrieval (mock)
│   │   ├── reasoning.py         # MiniMax m2.7 clinical reasoning + fallback
│   │   ├── fhir.py              # FHIR DiagnosticReport generation
│   │   └── uhi.py              # UHI doctor discovery & booking
│   │
│   ├── api/                     # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── main.py              # App entry, /health, /chat/message, serves chat UI
│   │   ├── callbacks.py         # UHI webhook handlers (/on_search, /on_confirm)
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── endpoints.py         # Dashboard API (patients, doctors, stats, book)
│   │   └── uhi_client.py       # ABDM UHI Gateway HTTP client (async, with retry)
│   │
│   ├── db/                      # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py        # Lazy async engine (SQLite dev / PostgreSQL prod)
│   │   └── models.py           # Patient, Session, Appointment (with indexes)
│   │
│   ├── fhir/                   # FHIR R4 resources
│   │   ├── __init__.py
│   │   └── generators.py       # DiagnosticReport & Observation builders
│   │
│   ├── graph/                  # LangGraph state machine
│   │   ├── __init__.py
│   │   └── state.py            # StateGraph with callable node functions & routing
│   │
│   ├── mcp/                    # Model Context Protocol (placeholder)
│   │   ├── __init__.py
│   │   └── whatsapp.py         # WhatsApp MCP (unused — web chat replaces this)
│   │
│   └── ui/                     # Frontend
│       ├── chat/               # Web chat interface (served by FastAPI)
│       │   └── index.html      # Single-file dark-themed healthcare chat UI
│       └── 3d-experience/      # React Three Fiber 3D dashboard (Next.js)
│           ├── app/
│           ├── components/
│           ├── package.json
│           └── ...
│
├── data/
│   └── patients.json           # Seed patient data (6 patients, 6 demo scenarios)
│
├── tests/
│   └── docsync_testing.ipynb   # Jupyter testing notebook
│
├── skills_agents/              # (READ ONLY - external skills reference)
│
├── requirements.txt            # Python dependencies (including aiosqlite)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore
├── README.md                   # Project documentation
├── ImplementationPlan.md       # This file
├── Checkpoints.md              # Progress tracking
└── PLAN_brid.md                # Architect's macro-plan
```

## LangGraph Pipeline (Working)

```
Patient Message (Web Chat UI → POST /chat/message)
       │
       ▼
┌─────────────────┐
│  steward_node   │ ← Red flag detection (chest pain, stroke, breathing, etc.)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
EMERGENCY   SYMPTOM
    │         │
    ▼         ▼
emergency_  symptom_node ← NLP extraction (8 categories)
   node          │
    │            ▼
    │     ┌──────────┐
    │     │  history  │ ← Mock patient records
    │     │   _node   │
    │     └────┬─────┘
    │          ▼
    │     ┌──────────┐
    │     │ reasoning │
    │     │  _node    │ ← MiniMax m2.7 (with mock fallback)
    │     └────┬─────┘
    │          │
    │     ┌────┴────┐
    │     │         │
    │     ▼         ▼
    │  ask_patient  fhir_node ← FHIR DiagnosticReport
    │  (confidence  │
    │   < 0.8)      ▼
    │          ┌─────────────┐
    │          │   uhi_      │
    │          │ discovery   │ ← Mock doctor search (3 doctors)
    │          └──────┬─────┘
    │                 │
    │          ┌──────┴──────┐
    │          │             │
    │          ▼             ▼
    │    uhi_confirm        END (no doctor selected)
    │          │
    │          ▼
    │    notify_patient
    │          │
    ▼          ▼
    END       END
```

## Bugs Fixed (This Session)

| # | Severity | File | Bug | Fix |
|---|----------|------|-----|-----|
| 1 | 🔴 CRITICAL | `graph/state.py` | `add_node()` passed strings instead of callables | Import actual node functions inside `create_graph()` |
| 2 | 🔴 CRITICAL | `graph/state.py` | Conflicting edges: both fixed edge AND conditional from `reasoning` | Removed `add_edge("reasoning", "fhir")` — conditional handles routing |
| 3 | 🟠 HIGH | `db/connection.py` | `psycopg2` (sync) used with `create_async_engine` | Lazy init + SQLite via `aiosqlite` for dev |
| 4 | 🟠 HIGH | `mcp/whatsapp.py` | `config.whats_app` doesn't exist | Changed to `config.messaging` |
| 5 | 🟡 MEDIUM | `agents/__init__.py` | Duplicate `emergency_node` import from both steward.py and emergency.py | Removed stale import from steward.py |
| 6 | 🟡 MEDIUM | `config.py` | Hardcoded `gpt-4o-mini` rejected by MiniMax | Env-configurable via `OPENAI_MODEL` |
| 7 | 🟡 MEDIUM | `src/__init__.py` | Missing package marker | Created file |
| 8 | 🟡 MEDIUM | `api/main.py` | LangGraph returns dict (Pydantic v2), code assumed object attrs | Changed to `result.get()` dict access |

## Task List

### Phase 1: Foundation & Safety ✅ COMPLETED
- [x] Project skeleton, requirements, config
- [x] Stewardship node (red flag detection for 5 emergency types)
- [x] Emergency node with context-specific instructions

### Phase 2: Core Patient Flow ✅ COMPLETED
- [x] Symptom node (NLP extraction, 8 categories, duration, severity)
- [x] History node (mock patient records)

### Phase 3: Diagnostic Reasoning & Reporting ✅ COMPLETED
- [x] Reasoning node (MiniMax m2.7 with lazy init + mock fallback)
- [x] FHIR R4 DiagnosticReport generation (plain dict, avoids validation issues)

### Phase 4: Doctor Discovery & Booking ✅ COMPLETED
- [x] UHI client with async HTTP, retry logic, mock fallback
- [x] UHI webhook callback handlers
- [x] Notify patient node

### Phase 5: Frontend ✅ COMPLETED
- [x] Web chat UI (dark-themed single-file HTML/CSS/JS at `/chat`)
- [x] Chat communicates with `/chat/message` API endpoint
- [x] Displays: symptoms, doctor cards, FHIR report toggle, emergency alerts
- [x] Sidebar shows session info, confidence bar, medical history
- [x] React Three Fiber 3D dashboard (separate, at `src/ui/3d-experience/`)

### Phase 6: Integration & Testing ✅ COMPLETED
- [x] LangGraph pipeline compiles and runs end-to-end
- [x] Both normal and emergency paths verified via curl
- [x] FastAPI server starts and serves all endpoints
- [x] Chat UI loads and communicates with backend
- [x] Patient seed data created (`data/patients.json`)

### Phase 7: Production Readiness ⏳ TODO
- [ ] Wire `history_node` to load from `data/patients.json` (or SQLite)
- [ ] Initialize SQLite DB with seed patient data
- [ ] Connect dashboard API (`endpoints.py`) to real database
- [ ] Add real UHI sandbox credentials
- [ ] Add Langfuse observability traces
- [ ] Add rate limiting to API endpoints
- [ ] Add input sanitization for patient messages
- [ ] Multi-language support (Kannada/Hindi)

## Verified Endpoints

| Method | Endpoint | Status | Description |
|--------|----------|--------|-------------|
| GET | `/` | ✅ Working | Serves chat UI |
| GET | `/chat` | ✅ Working | Serves chat UI |
| GET | `/health` | ✅ Working | Returns `{"status": "healthy", ...}` |
| POST | `/chat/message` | ✅ Working | Full LangGraph pipeline (~15-25s with LLM) |
| GET | `/api/patients` | ✅ Working | Mock patient list for dashboard |
| GET | `/api/doctors` | ✅ Working | Mock doctor list for dashboard |
| GET | `/api/stats` | ✅ Working | Dashboard statistics |
| POST | `/api/book` | ✅ Working | Mock booking endpoint |
| POST | `/uhi/on_search` | ✅ Working | UHI search callback |
| POST | `/uhi/on_confirm` | ✅ Working | UHI confirm callback |

## Patient Seed Data

Six patients in `data/patients.json` covering:

| Patient | Age | Conditions | Demo Scenario |
|---------|-----|------------|---------------|
| Ravi Shankar | 52 | Diabetes, Hypertension | Normal: headache + blurred vision |
| Ananya Iyer | 28 | Asthma, Anemia | Emergency: breathing difficulty |
| Mohammed Farhan | 45 | Heart Disease (stent) | Emergency: chest pain |
| Lakshmi Devi | 67 | Osteoarthritis, Diabetes | Normal: severe joint pain |
| Arjun Nair | 19 | None (new patient) | Normal: fever + COVID exposure |
| Priya Menon | 34 | Anxiety, Migraines | Emergency: stroke symptoms |

## Database Schema (Defined, Not Yet Active)

```sql
-- Patients table (src/db/models.py)
CREATE TABLE patients (
    id VARCHAR PRIMARY KEY,
    phone_number VARCHAR UNIQUE,
    name VARCHAR,
    medical_history JSON DEFAULT '[]',
    allergies JSON DEFAULT '[]',
    current_medications JSON DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sessions table
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    patient_id VARCHAR REFERENCES patients(id),
    raw_message TEXT,
    symptoms JSON DEFAULT '[]',
    symptom_duration VARCHAR,
    severity VARCHAR,
    clinical_findings JSON DEFAULT '[]',
    confidence_score FLOAT,
    fhir_report_id VARCHAR,
    appointment_id VARCHAR,
    booking_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Appointments table
CREATE TABLE appointments (
    id VARCHAR PRIMARY KEY,
    patient_id VARCHAR REFERENCES patients(id),
    doctor_id VARCHAR,
    doctor_name VARCHAR,
    hospital VARCHAR,
    status VARCHAR DEFAULT 'pending',
    fhir_report_id VARCHAR,
    requested_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP
);
```

## How to Run

### Start the API + Chat UI
```bash
cd /home/syed/AI-Ignite/AI-Ignite-DocSync-Agent
source .venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Open http://localhost:8000/chat in browser
```

### Quick Pipeline Test (Terminal)
```bash
python -c "
from src.graph.state import create_graph, PatientState

graph = create_graph()

# Normal path
state = PatientState(raw_message='I have headache for 3 days', phone_number='+919876543210')
result = graph.invoke(state)
print(f'Symptoms: {result[\"symptoms\"]}')
print(f'Doctors: {len(result[\"doctor_options\"])}')

# Emergency path
state2 = PatientState(raw_message='severe chest pain', phone_number='+919876543210')
result2 = graph.invoke(state2)
print(f'Emergency: {result2[\"has_red_flags\"]}')
print(f'Message: {result2[\"error_message\"]}')
"
```

### 3D Dashboard (Optional)
```bash
cd src/ui/3d-experience
npm install
npm run dev
# Open http://localhost:3000
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| MiniMax API latency (15-25s) | High | Mock fallback if LLM unavailable; typing indicator in UI |
| Clinical hallucinations | High | Stewardship node + Diagnostic Gap pattern + confidence scoring |
| No real UHI credentials | Med | Full mock data pipeline; swap when sandbox access available |
| SQLite concurrency limits | Low | Sufficient for prototype; PostgreSQL ready for production |

## Known Limitations

1. **History Node** — Returns hardcoded mock data (not yet loading from `patients.json`)
2. **MiniMax m2.7** — Model name may need adjustment; JSON parsing sometimes fails (fallback works)
3. **Database** — Schema defined but not initialized; queries use mock data
4. **UHI Gateway** — Returns mock doctors (no real ABDM sandbox credentials)
5. **WhatsApp MCP** — Placeholder only; web chat is the active interface

---

*Built for the AI Ignite Hackathon - HKBK College*
