# Implementation Plan: DocSync (Healthcare Coordination Agent)

## Overview
DocSync is an intermediate healthcare coordination agent that bridges patients on WhatsApp to doctors via a specialized dashboard and ABDM UHI APIs. It uses LangGraph to orchestrate symptom intake, history retrieval, diagnostic reasoning (MiniMax m2.7), and appointment booking.

## Architecture Decisions
- **Orchestration:** LangGraph (Python) for stateful, cyclic clinical reasoning.
- **Reasoning Engine:** MiniMax m2.7 for high-fidelity tool-calling and FHIR formatting.
- **Database:** PostgreSQL on Railway for longitudinal patient memory.
- **Messaging:** WhatsApp via `verygoodplugins/whatsapp-mcp` (Model Context Protocol).
- **Standards:** FHIR (Fast Healthcare Interoperability Resources) for all clinical reports.
- **Discovery:** ABDM Unified Health Interface (UHI) for doctor search and booking.

## Task List

### Phase 1: Foundation & Safety
- [ ] **Task 1: Project Skeleton & Environment**
    - **Description:** Setup Python environment, install dependencies, and configure `.env` with Langfuse and MiniMax keys.
    - **Acceptance criteria:** `pip install -r requirements.txt` succeeds; `.env` is validated.
    - **Files likely touched:** `requirements.txt`, `.env`.
    - **Estimated scope:** XS.
- [ ] **Task 2: Stewardship Node (Safety First)**
    - **Description:** Implement the `steward_node` to intercept medical emergencies (Red Flags).
    - **Acceptance criteria:** Correctly identifies "chest pain" or "stroke" and routes to `emergency_node`.
    - **Files likely touched:** `src/agents/steward.py`.
    - **Estimated scope:** S.

### Phase 2: Core Patient Flow
- [ ] **Task 3: Symptom Intake Node**
    - **Description:** Build the `symptom_node` to extract symptoms from WhatsApp messages using Pydantic schemas.
    - **Acceptance criteria:** Extracts structured JSON (symptoms, duration, severity) from raw text.
    - **Files likely touched:** `src/agents/symptoms.py`, `src/schemas/symptoms.py`.
    - **Estimated scope:** S.
- [ ] **Task 4: Historical Context Node**
    - **Description:** Build the `history_node` to query the database for past patient records.
    - **Acceptance criteria:** Successfully retrieves and injects history into the graph state.
    - **Files likely touched:** `src/agents/history.py`, `src/db/models.py`.
    - **Estimated scope:** S.

### Phase 3: Diagnostic Reasoning & Reporting
- [ ] **Task 5: Reasoning Node (MiniMax m2.7)**
    - **Description:** Implement clinical reasoning using the "Diagnostic Gap" pattern.
    - **Acceptance criteria:** Agent asks clarifying questions if confidence is low; produces findings if high.
    - **Files likely touched:** `src/agents/reasoning.py`.
    - **Estimated scope:** M.
- [ ] **Task 6: FHIR Report Generator**
    - **Description:** Use `fhir.resources` to format reasoning output into a DiagnosticReport.
    - **Acceptance criteria:** Generates a valid FHIR JSON document.
    - **Files likely touched:** `src/schemas/fhir_reports.py`, `src/agents/fhir_node.py`.
    - **Estimated scope:** S.

### Phase 4: Doctor Discovery & Booking
- [ ] **Task 7: UHI API Integration**
    - **Description:** Implement ABDM UHI `/search` and `/on_search` callback logic.
    - **Acceptance criteria:** Successfully fetches doctor catalogs from the UHI Gateway.
    - **Files likely touched:** `src/api/uhi_client.py`, `src/api/callbacks.py`.
    - **Estimated scope:** L.
- [ ] **Task 8: WhatsApp Handoff (MCP)**
    - **Description:** Connect the final booking confirmation to the WhatsApp MCP server.
    - **Acceptance criteria:** Patient receives appointment details on WhatsApp.
    - **Files likely touched:** `src/mcp/whatsapp_server.py`.
    - **Estimated scope:** M.

## Checkpoints

### Checkpoint 1: Safety & Intake
- [ ] `steward_node` and `symptom_node` pass unit tests.
- [ ] Basic graph traversal from intake to history works.

### Checkpoint 2: Reasoning & Reporting
- [ ] MiniMax m2.7 produces valid FHIR reports.
- [ ] Diagnostic Gap loop correctly handles follow-up questions.

### Checkpoint 3: End-to-End
- [ ] UHI discovery returns results.
- [ ] Full flow from WhatsApp symptom to WhatsApp confirmation is verified in logs.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| ABDM UHI Asynchronous Lag | High | Implement robust retry logic and state persistence in LangGraph. |
| Clinical Hallucinations | High | Use the "Diagnostic Gap" pattern and Stewardship node. |
| WhatsApp API Rate Limits | Med | Implement message queuing in the MCP layer. |

## Open Questions
- What is the exact Sandbox Client ID for the HKBK hackathon UHI gateway?
- Do we need to support multiple languages (Kannada/Hindi) for symptom intake?
