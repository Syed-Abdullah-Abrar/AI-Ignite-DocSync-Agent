# DocSync - Healthcare Coordination Agent

> AI-powered healthcare coordination bridging WhatsApp patients to doctors via ABDM UHI APIs

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-purple.svg)](https://langchain.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

DocSync is an intermediate healthcare coordination agent that bridges patients on WhatsApp to doctors via a specialized dashboard and ABDM UHI APIs. It uses LangGraph to orchestrate:

- **Symptom intake** via WhatsApp NLP
- **Historical context** retrieval from PostgreSQL
- **Clinical reasoning** with MiniMax m2.7
- **FHIR R4** diagnostic reports
- **Doctor discovery & booking** via ABDM UHI

## Architecture

```
Patient (WhatsApp) 
       │
       ▼
┌─────────────────┐
│  steward_node   │ ← Red flag detection (emergencies)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  symptom_node   │ ← NLP symptom extraction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  history_node  │ ← Patient medical history
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ reasoning_node  │ ← MiniMax m2.7 clinical reasoning
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    fhir_node    │ ← FHIR DiagnosticReport
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ uhi_discovery   │ ← ABDM UHI doctor search
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ uhi_confirm     │ ← Appointment booking
└────────┬────────┘
         │
         ▼
   Doctor Dashboard
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Orchestration | LangGraph (Python) |
| Reasoning Engine | MiniMax m2.7 |
| Database | PostgreSQL (Railway) |
| Messaging | WhatsApp MCP |
| Clinical Standards | FHIR R4 |
| Discovery & Booking | ABDM UHI Gateway |
| API | FastAPI |
| Dashboard | React Three Fiber (3D) |
| Observability | Langfuse |

## Project Structure

```
DocSync/
├── src/
│   ├── agents/              # LangGraph nodes (clinical logic)
│   │   ├── steward.py      # Red flag detection
│   │   ├── symptom.py      # Symptom extraction (NLP)
│   │   ├── history.py      # Patient medical history
│   │   ├── reasoning.py    # MiniMax m2.7 clinical reasoning
│   │   ├── fhir.py         # FHIR DiagnosticReport generation
│   │   ├── uhi.py          # ABDM UHI doctor discovery/booking
│   │   └── emergency.py    # Emergency routing
│   ├── api/                # FastAPI endpoints
│   │   ├── main.py         # App entry, /health, /whatsapp/webhook
│   │   ├── callbacks.py    # UHI webhook handlers
│   │   ├── schemas.py      # Pydantic request/response models
│   │   └── uhi_client.py  # UHI Gateway HTTP client
│   ├── db/                  # Database layer
│   │   ├── connection.py   # Async PostgreSQL (SQLAlchemy)
│   │   └── models.py       # Patient, Session, Appointment
│   ├── fhir/
│   │   └── generators.py   # FHIR R4 resource builders
│   ├── graph/
│   │   └── state.py        # LangGraph StateGraph definition
│   ├── mcp/
│   │   └── whatsapp.py     # WhatsApp MCP integration
│   └── config.py           # Environment config (dataclasses)
├── tests/
│   └── docsync_testing.ipynb  # Jupyter testing notebook
├── src/ui/3d-experience/   # React Three Fiber 3D dashboard
│   ├── components/          # R3F 3D components
│   ├── app/                 # Next.js pages
│   └── ...
├── requirements.txt
└── .env.example
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for 3D dashboard)
- PostgreSQL database
- MiniMax API key
- ABDM UHI sandbox credentials (optional)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd DocSync

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

```bash
# .env
MINIMAX_API_KEY=your_minimax_api_key
OPENAI_API_BASE=https://api.minimax.io/v1

UHI_CLIENT_ID=your_uhi_client_id
UHI_CLIENT_SECRET=your_uhi_client_secret
UHI_GATEWAY_URL=https://sandbox.abdm.gov.in/uhi/gateway
CALLBACK_URL=https://your-domain.com/uhi/callback

DATABASE_URL=postgresql://user:password@localhost:5432/ayusync

LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Running the API

```bash
# Start FastAPI server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# API documentation at http://localhost:8000/docs
```

### Running the 3D Dashboard

```bash
# Navigate to 3D UI
cd src/ui/3d-experience

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Testing in Jupyter

```bash
# Install Jupyter
pip install jupyter ipykernel

# Add environment as Jupyter kernel
python -m ipykernel install --user --name=docsync --display-name="DocSync"

# Start Jupyter
jupyter notebook tests/docsync_testing.ipynb

# Or with JupyterLab
jupyter lab tests/docsync_testing.ipynb
```

### Quick Test (No Jupyter)

```bash
python -c "
from src.graph.state import PatientState
from src.agents.steward import steward_node
from src.agents.symptom import symptom_node

# Test emergency detection
state = PatientState(raw_message='I have chest pain', phone_number='+919876543210')
result = steward_node(state)
print(f'Emergency detected: {result.has_red_flags}')

# Test symptom extraction  
state2 = PatientState(raw_message='I have headache for 3 days', phone_number='+919876543210')
result2 = symptom_node(state2)
print(f'Symptoms: {result2.symptoms}')
"
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Test Coverage

| Node | Coverage |
|------|----------|
| steward_node | Red flag patterns for 5 emergency types |
| symptom_node | 8 symptom categories with NLP extraction |
| history_node | Patient lookup and mock data |
| fhir_node | FHIR R4 DiagnosticReport generation |
| uhi_discovery | Mock doctor search |
| uhi_confirm | Booking confirmation flow |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/whatsapp/webhook` | WhatsApp message webhook |
| POST | `/uhi/on_search` | UHI search callback |
| POST | `/uhi/on_confirm` | UHI booking callback |

## FHIR Report Format

```json
{
  "id": "report-{session_id}",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "72198-7",
      "display": "Consultation note"
    }]
  },
  "subject": {
    "reference": "Patient/{phone_number}"
  },
  "contained": [...]
}
```

## Red Flag Detection

The steward node detects these emergency patterns:

| Category | Keywords |
|----------|----------|
| Chest Pain | chest pain, chest pressure, arm pain, jaw pain |
| Stroke | face drooping, slurred speech, numbness one side |
| Breathing | difficulty breathing, shortness of breath, choking |
| Bleeding | severe bleeding, blood in stool/vomit |
| Consciousness | unconscious, fainted, seizure |

## Development

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all public functions

### Commit Messages

```
feat: add new symptom extraction patterns
fix: resolve emergency routing edge case  
docs: update API documentation
test: add FHIR generation tests
refactor: simplify history node queries
```

## License

MIT License - see LICENSE file

---

*Built for the AI Ignite Hackathon - HKBK College*
