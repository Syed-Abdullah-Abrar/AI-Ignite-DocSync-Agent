# Implementation Plan: DocSync (Healthcare Coordination Agent)

> Last Updated: 2024

## Overview

DocSync is an intermediate healthcare coordination agent that bridges patients on WhatsApp to doctors via a specialized dashboard and ABDM UHI APIs. It uses LangGraph to orchestrate symptom intake, history retrieval, diagnostic reasoning (MiniMax m2.7), and appointment booking.

## Architecture Decisions

- **Orchestration:** LangGraph (Python) for stateful, cyclic clinical reasoning.
- **Reasoning Engine:** MiniMax m2.7 for high-fidelity tool-calling and FHIR formatting.
- **Database:** PostgreSQL on Railway for longitudinal patient memory.
- **Messaging:** WhatsApp via `verygoodplugins/whatsapp-mcp` (Model Context Protocol).
- **Standards:** FHIR (Fast Healthcare Interoperability Resources) for all clinical reports.
- **Discovery:** ABDM Unified Health Interface (UHI) for doctor search and booking.
- **Dashboard:** React Three Fiber for 3D visualization.

## Current Project Structure

```
DocSync/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Environment configuration (dataclasses)
│   │
│   ├── agents/                  # LangGraph nodes
│   │   ├── __init__.py
│   │   ├── steward.py          # Red flag detection (emergency triage)
│   │   ├── emergency.py         # Emergency routing & messaging
│   │   ├── symptom.py           # NLP symptom extraction
│   │   ├── history.py           # Patient medical history retrieval
│   │   ├── reasoning.py         # MiniMax m2.7 clinical reasoning
│   │   ├── fhir.py             # FHIR DiagnosticReport generation
│   │   └── uhi.py              # UHI doctor discovery & booking
│   │
│   ├── api/                     # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── main.py              # App entry, /health, /whatsapp/webhook
│   │   ├── callbacks.py         # UHI webhook handlers (/on_search, /on_confirm)
│   │   ├── schemas.py           # Pydantic request/response models
│   │   └── uhi_client.py       # ABDM UHI Gateway HTTP client (async)
│   │
│   ├── db/                      # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py        # SQLAlchemy async PostgreSQL connection
│   │   └── models.py           # Patient, Session, Appointment (with indexes)
│   │
│   ├── fhir/                   # FHIR R4 resources
│   │   ├── __init__.py
│   │   └── generators.py       # DiagnosticReport & Observation builders
│   │
│   ├── graph/                  # LangGraph state machine
│   │   ├── __init__.py
│   │   └── state.py           # StateGraph definition with routing logic
│   │
│   ├── mcp/                    # Model Context Protocol
│   │   ├── __init__.py
│   │   └── whatsapp.py         # WhatsApp messaging integration
│   │
│   └── ui/                     # Frontend
│       └── 3d-experience/      # React Three Fiber 3D dashboard
│           ├── app/
│           │   ├── layout.tsx
│           │   └── page.tsx
│           ├── components/
│           │   ├── Scene.tsx       # Main 3D scene
│           │   ├── HealthHub.tsx    # Central coordination hub
│           │   ├── PatientNode.tsx  # Patient 3D nodes
│           │   ├── DoctorNode.tsx   # Doctor 3D nodes
│           │   ├── ConnectionLines.tsx # Dynamic connections
│           │   ├── Loader.tsx      # Loading indicator
│           │   └── Interface.tsx    # 2D overlay UI
│           ├── package.json
│           ├── tsconfig.json
│           ├── next.config.js
│           └── README.md
│
├── tests/
│   └── docsync_testing.ipynb   # Comprehensive Jupyter testing notebook
│
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── README.md                    # Project documentation
├── ImplementationPlan.md        # This file
└── Checkpoints.md              # Progress tracking
```

## LangGraph Pipeline (Current State)

```
Patient Message (WhatsApp)
       │
       ▼
┌─────────────────┐
│  steward_node   │ ← Red flag detection (chest pain, stroke, etc.)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
EMERGENCY   SYMPTOM
    │         │
    ▼         ▼
emergency_  symptom_node ← NLP extraction
   node          │
    │            ▼
    │     ┌──────────┐
    │     │  history  │
    │     │   _node   │
    │     └────┬─────┘
    │          ▼
    │     ┌──────────┐
    │     │ reasoning │
    │     │  _node    │ ← MiniMax m2.7
    │     └────┬─────┘
    │          │
    │          ▼
    │     ┌─────────┐
    │     │   fhir  │
    │     │  _node   │ ← FHIR DiagnosticReport
    │     └────┬────┘
    │          ▼
    │     ┌─────────────┐
    │     │   uhi_     │
    │     │ discovery   │ ← ABDM UHI doctor search
    │     └──────┬─────┘
    │            ▼
    │     ┌─────────────┐
    │     │   uhi_      │
    │     │   confirm   │ ← Appointment booking
    │     └──────┬─────┘
    │            ▼
    │     ┌─────────────┐
    │     │   notify_   │
    │     │  patient    │ ← WhatsApp notification
    │     └──────┬─────┘
    │            │
    ▼            ▼
    END         END
```

## Task List

### Phase 1: Foundation & Safety ✅ COMPLETED
- [x] **Task 1: Project Skeleton & Environment**
    - ✅ `requirements.txt` with all dependencies
    - ✅ `.env.example` configuration template
    - ✅ `src/config.py` with dataclasses
    
- [x] **Task 2: Stewardship Node (Safety First)**
    - ✅ `steward_node` detects red flags (chest pain, stroke, breathing, bleeding, consciousness)
    - ✅ `emergency_node` routes to emergency services

### Phase 2: Core Patient Flow ✅ COMPLETED
- [x] **Task 3: Symptom Intake Node**
    - ✅ `symptom_node` extracts symptoms, duration, severity
    - ✅ 8 symptom categories with NLP patterns
    
- [x] **Task 4: Historical Context Node**
    - ✅ `history_node` retrieves patient records
    - ✅ Mock data for development

### Phase 3: Diagnostic Reasoning & Reporting ✅ COMPLETED
- [x] **Task 5: Reasoning Node (MiniMax m2.7)**
    - ✅ `reasoning_node` with Diagnostic Gap pattern
    - ✅ Lazy LLM initialization
    - ✅ Error handling with fallback
    
- [x] **Task 6: FHIR Report Generator**
    - ✅ `fhir_node` generates DiagnosticReport
    - ✅ `generators.py` for FHIR R4 compliant resources
    - ✅ Plain dict output (avoids fhir.resources validation issues)

### Phase 4: Doctor Discovery & Booking ✅ COMPLETED
- [x] **Task 7: UHI API Integration**
    - ✅ `uhi_client.py` with async HTTP client
    - ✅ Retry logic with exponential backoff
    - ✅ Mock data for development (no credentials required)
    
- [x] **Task 8: WhatsApp Handoff**
    - ✅ `whatsapp.py` MCP integration
    - ✅ Message formatting templates

### Phase 5: Frontend & Dashboard 🚧 IN PROGRESS
- [x] **Task 9: 3D Dashboard**
    - ✅ React Three Fiber implementation
    - ✅ Patient/Doctor nodes with animations
    - ✅ Connection lines visualization
    - ✅ 2D overlay interface
    - ⏳ Connect to backend API

### Phase 6: Testing & Integration ⏳ PENDING
- [ ] **Task 10: End-to-End Testing**
    - ⏳ Jupyter notebook tests pass
    - ⏳ API endpoint tests
    - ⏳ WhatsApp MCP integration
    
- [ ] **Task 11: Database Connection**
    - ⏳ Connect to PostgreSQL
    - ⏳ Run migrations
    - ⏳ Verify queries with indexes

## Checkpoints

### Checkpoint 1: Safety & Intake ✅ VERIFIED
- [x] `steward_node` correctly routes emergencies
- [x] `symptom_node` extracts symptoms, duration, severity
- [x] Basic graph traversal from intake to history works

### Checkpoint 2: Reasoning & Reporting ✅ VERIFIED
- [x] FHIR reports generated in correct format
- [x] Diagnostic Gap loop correctly handles follow-up questions

### Checkpoint 3: Doctor Discovery ✅ VERIFIED
- [x] Mock doctors returned successfully
- [x] Booking confirmation works

### Checkpoint 4: Frontend ✅ CREATED
- [x] 3D scene renders with patient/doctor nodes
- [x] Interactive selection working
- ⏳ Connect to backend for real data

### Checkpoint 5: Integration ⏳ PENDING
- ⏳ UHI discovery returns real results
- ⏳ Full WhatsApp symptom to confirmation verified

## Database Schema (Optimized)

```sql
-- Patients table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR UNIQUE,
    name VARCHAR,
    medical_history JSONB DEFAULT '[]',
    allergies JSONB DEFAULT '[]',
    current_medications JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_patients_phone ON patients(phone_number);

-- Sessions table
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    symptoms JSONB DEFAULT '[]',
    confidence_score FLOAT,
    fhir_report_id VARCHAR,
    booking_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_sessions_patient_created ON sessions(patient_id, created_at);

-- Appointments table
CREATE TABLE appointments (
    id VARCHAR PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    doctor_id VARCHAR,
    doctor_name VARCHAR,
    hospital VARCHAR,
    status VARCHAR DEFAULT 'pending',
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ
);
CREATE INDEX idx_appointments_status ON appointments(status);
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ABDM UHI Asynchronous Lag | High | Implemented retry logic with exponential backoff |
| Clinical Hallucinations | High | Stewardship node + Diagnostic Gap pattern |
| WhatsApp API Rate Limits | Med | Message queuing ready in MCP layer |
| Jupyter Event Loop Conflict | Med | ThreadPoolExecutor for async calls from sync context |

## Known Limitations

1. **UHI Gateway** - Returns mock data (no real ABDM sandbox credentials)
2. **MiniMax m2.7** - Basic integration (no structured output parsing)
3. **Database** - Queries use mock data (no real PostgreSQL connection)
4. **WhatsApp MCP** - Placeholder (no actual message sending)
5. **3D Dashboard** - Static sample data (not connected to backend)

## Open Questions

- [ ] What is the exact Sandbox Client ID for the HKBK hackathon UHI gateway?
- [ ] Do we need to support multiple languages (Kannada/Hindi) for symptom intake?
- [ ] Should we implement conversation context (follow-up questions)?
- [ ] Real WhatsApp Business API credentials available?

## How to Test

### Quick Test (Terminal)
```bash
python -c "
from src.graph.state import PatientState
from src.agents.steward import steward_node
from src.agents.symptom import symptom_node

# Emergency test
state = PatientState(raw_message='I have chest pain', phone_number='+919876543210')
result = steward_node(state)
print(f'Emergency: {result.has_red_flags}')

# Symptom test
state = PatientState(raw_message='I have headache for 3 days', phone_number='+919876543210')
result = symptom_node(state)
print(f'Symptoms: {result.symptoms}')
"
```

### Jupyter Notebook
```bash
cd tests
jupyter notebook docsync_testing.ipynb
```

### 3D Dashboard
```bash
cd src/ui/3d-experience
npm install
npm run dev
# Open http://localhost:3000
```

### API Server
```bash
uvicorn src.api.main:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

---

*Built for the AI Ignite Hackathon - HKBK College*
