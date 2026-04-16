# 🏥 DocSync

**DocSync** is an advanced AI healthcare coordination agent built for the **AI Ignite Hackathon** at HKBK College of Engineering. It serves as a seamless, fast intermediate channel between patients and doctors, leveraging multi-agent orchestration to provide clinical reasoning, historical context, and automated appointment booking.

---

## 🌟 Vision: AI for Impact
In the bustling healthcare landscape of Bangalore, the gap between a patient's initial symptoms and a doctor's consultation can be fraught with delays and loss of clinical context. **DocSync** bridges this gap by:
1. **Empowering Patients:** Providing an intuitive WhatsApp interface for symptom reporting.
2. **Empowering Doctors:** Delivering structured, FHIR-compliant clinical reports before the patient even walks in.
3. **Synchronizing Care:** Automating doctor discovery and booking via India's **ABDM Unified Health Interface (UHI)** protocols.

---

## 🚀 Key Features
- **WhatsApp Intake (MCP):** Patients communicate naturally with the agent via WhatsApp.
- **Agentic Reasoning (LangGraph):** A multi-node state machine routes information through symptom analysis, history retrieval, and diagnostic reasoning.
- **Clinical History Retrieval:** Maintains long-term memory of a patient's previous illnesses and states for better longitudinal care.
- **FHIR Reporting:** Automatically structures patient data into the global **Fast Healthcare Interoperability Resources (FHIR)** standard.
- **UHI Discovery & Booking:** Integrates with the **Ayushman Bharat Digital Mission (ABDM)** to search for verified doctors and book real-time appointments.
- **Human-in-the-Loop:** A robust confirmation bridge ensuring medical safety and data accuracy.

---

## 🛠 Technology Stack
- **AI Orchestration:** [LangGraph](https://www.langchain.com/langgraph)
- **Reasoning Engine:** [MiniMax m2.7](https://www.minimax.io/) (High-performance building & tool-calling)
- **Planning & Validation:** [Gemini 3.1 Pro](https://deepmind.google/technologies/gemini/) (Macro-planning & testing)
- **Integration Framework:** [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for WhatsApp.
- **Healthcare Standards:** `fhir.resources` (Python), ABDM UHI APIs.
- **Frontend/Dashboard:** [Google Stitch](https://stitch.google.com/) (Rapid UI/UX generation) & Next.js.
- **Deployment:** [Railway](https://railway.app/) (Backend/DB) & [Vercel](https://vercel.com/) (Frontend).
- **Observability:** [Langfuse](https://langfuse.com/).

---

## 🏗 Architecture
```text
[Patient (WhatsApp)] 
      |
      v
[WhatsApp MCP Server] 
      |
      v
[LangGraph State Machine] <--- [Historical Data (PostgreSQL)]
      | (Nodes: Symptom -> History -> Reasoning -> Booking)
      v
[MiniMax m2.7 Reasoning] ----> [FHIR Report Generator]
      |                              |
      v                              v
[ABDM UHI APIs] -------------> [Doctor Dashboard (Vercel)]
      |                              |
      v                              v
[Appointment Booked] <-------- [Doctor Confirmation]
```

---

## 📦 Project Structure
- `/src/agents/`: Core LangGraph node definitions.
- `/src/mcp/`: WhatsApp integration and MCP servers.
- `/src/schemas/`: FHIR-compliant data models.
- `/src/ui/`: Doctor-facing dashboard (Next.js).
- `/tests/`: Automated testing and agent trace logs.

---

## 🏁 Getting Started
(Detailed installation instructions to follow during development)

---

## ⚖️ Disclaimer
*DocSync is an AI-powered coordination tool. For actual medical advice, diagnosis, or treatment, always consult a qualified healthcare professional.*

---

**Developed for AI Ignite Hackathon @ HKBK College of Engineering**
