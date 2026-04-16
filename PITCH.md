# DocSync — Hackathon Pitch Script

> **Total Time:** ~8 minutes (3 min intro + 5 min live demo)
> **URL:** `http://localhost:8000/chat`
> **Start command:** `uvicorn src.api.main:app --host 0.0.0.0 --port 8000`

---

## 🎤 PART 1: THE HOOK (30 seconds)

> *"Every 4 seconds, someone in India searches Google for their symptoms instead of calling a doctor. 63% of Indians in tier-2 and tier-3 cities have no access to specialist consultations within 50 kilometers.*
>
> *What if an AI agent could triage your symptoms, pull your medical history, reason like a doctor, generate a clinical report, and book the right specialist — all in under 30 seconds?"*
>
> ***"This is DocSync."***

---

## 🎤 PART 2: WHAT IS DOCSYNC (60 seconds)

> *"DocSync is an AI-powered healthcare coordination agent. It sits between the patient and the doctor, handling the entire journey from symptom intake to appointment booking.*
>
> *It uses a **LangGraph state machine** — not a single LLM call, but a pipeline of 7 specialized AI nodes that work together like a medical team."*

### Show the architecture (point to screen):

> *"Here's how it works:*
> 1. **Steward Node** — First-response triage. Detects red flags like chest pain or stroke symptoms in under 1 second.
> 2. **Symptom Node** — NLP extraction. Identifies what hurts, how long, how bad.
> 3. **History Node** — Pulls the patient's medical records — diabetes, allergies, medications.
> 4. **Reasoning Node** — This is the brain. MiniMax m2.7 performs differential diagnosis using the patient's full context.
> 5. **FHIR Node** — Generates a standards-compliant clinical report that any hospital system can read.
> 6. **UHI Discovery** — Searches for available doctors via India's Unified Health Interface.
> 7. **Booking Node** — Confirms the appointment.
>
> *All of this happens in one pipeline invocation. No manual handoffs. No dropped context."*

---

## 🎤 PART 3: THE PROBLEM WE SOLVE (30 seconds)

> *"Today, a patient calls a hospital, explains their symptoms to a receptionist, gets transferred, re-explains everything to a nurse, waits, then re-explains to the doctor. Their allergy to Penicillin? Buried in a paper file nobody checked.*
>
> *DocSync eliminates this. The doctor receives a FHIR-compliant report BEFORE the consultation — symptoms, history, allergies, differential diagnosis — everything."*

---

## 🎤 PART 4: LIVE DEMO (5 minutes)

> *"Let me show you. I have 6 real patient stories loaded in our database. Let's walk through them."*

**[Open http://localhost:8000/chat in browser]**

---

### 🟢 DEMO 1: Ravi Shankar — The Chronic Patient (Normal Flow)

> *"Meet Ravi. He's 52, a school teacher from Bangalore. He has Type 2 Diabetes and Hypertension — both managed with Metformin and Lisinopril. He's allergic to Penicillin. All of this is already in our database."*

**Type this message:**
```
I have been having a persistent headache for the past 3 days, along with blurred vision. My blood pressure readings at home show 165/95.
```

**While it's processing (15-20s), explain:**
> *"Right now, 7 nodes are executing in sequence:*
> - *The Steward checks for red flags — headache isn't an emergency*
> - *The Symptom node extracts 'headache' and 'pain'*
> - *The History node looks up Ravi's phone number → finds his Diabetes and Hypertension*
> - *The Reasoning engine feeds ALL of this to MiniMax m2.7 — symptoms + history + medications + allergies*
> - *It generates a FHIR DiagnosticReport*
> - *And finds 3 available doctors"*

**When the response arrives, point out:**
> - *"Look at the sidebar — his medical history loaded automatically because he selected his profile."*
> - *"The symptom cards appear, and notice it found doctors matching the differential diagnosis."*
> - *"Now click 'View Doctor's Report'. What you see first is a beautiful, Human-Readable AI Summary linking his headache to his hypertension medication. But beneath it is the raw FHIR R4 JSON. This is what makes it interoperable."*

### 🔄 THE HANDOFF: Patient → Doctor

> *"When the patient clicks 'Book', we don't just send a text message. Using India's ABDM UHI network, we send the booking confirmation WITH this attached FHIR payload straight into the doctor's existing software. Let's see what the doctor sees."*

**[Switch tabs to the Doctor View: http://localhost:8000/doctor]**

> *"This is Dr. Sharma's EMR Dashboard. Notice the glowing UHI Network Active badge. A new appointment just arrived for Ravi Shankar."*

**[Click on Ravi Shankar in the left queue]**

> *"Dr. Sharma doesn't get a blank slate. He gets the complete AI clinical handoff. He sees:*
> - *The AI's differential diagnosis.*
> - *Ravi's underlying diabetes and hypertension.*
> - *And a critical red alert: Penicillin Allergy.*
>
> *Before the patient even walks in the door, the doctor has a highly structured, accurate, and safe medical context.*"

**[Click 'Accept Appointment']**

> *"Here's the magic. When Dr. Sharma clicks Accept, we trigger a real-time UHI confirmation."*

**[A browser prompt will appear asking for a phone number. Type YOUR verified phone number (e.g., +919876543210) and hit Enter/OK]**

> *"DocSync instantly completes the handshake and fires a secure SMS notification back to the patient. I'm putting my own phone number in..."*

**[The Success Modal appears on screen. Hold up your phone to the judges or bring it on screen so they can see the SMS arrive!]**

> *"And there it is. The patient just received an SMS from the hospital: 'Hello Ravi Shankar, your appointment with Dr. Sharma has been confirmed...'. 
>
> That is a complete, closed-loop synchronous healthcare transaction, powered by AI and ABDM, in under 20 seconds."*

**[Switch back to the Patient chat tab]**

---

### 🔴 DEMO 2: Mohammed Farhan — The Emergency (Emergency Path)

> *"Now meet Farhan. He's 45, has known Coronary Artery Disease — he had a stent placed 2 years ago. He takes Aspirin, Atorvastatin, and Metoprolol. But today..."*

**Type this message:**
```
I'm having severe chest tightness and sweating. Pain is radiating to my left arm. I feel like something is very wrong.
```

**This responds INSTANTLY (<1 second). Point out:**
> *"Notice how fast that was. The Steward node detected 'chest pain' as a red flag and immediately routed to the Emergency node — skipping the entire diagnostic pipeline.*
>
> *It doesn't waste time extracting symptoms or booking doctors. It says: 'Call 108 immediately. Fortis Emergency: 080-66214444.'*
>
> *In a real-world deployment, this would simultaneously send an SMS, ping the nearest emergency room, and alert the patient's emergency contact. Every second counts."*

---

### 🟢 DEMO 3: Lakshmi Devi — Complex Multi-Drug Patient (Normal Flow)

> *"Lakshmi is 67 with three conditions — Osteoarthritis, Diabetes, and Hypothyroidism. She takes 4 medications daily. She's allergic to Ibuprofen AND Shellfish. This is the kind of patient where missing one detail can be dangerous."*

**Type this message:**
```
My knee pain is extremely bad today. Both knees are swollen and I feel exhausted. I could barely get out of bed.
```

**While processing, highlight:**
> *"This is where DocSync's value really shows. The reasoning engine doesn't just see 'knee pain' — it sees knee pain IN A PATIENT who takes Paracetamol, has diabetes affecting wound healing, and is allergic to Ibuprofen. No NSAID recommendation. No drug interactions. Context matters."*

---

### 🔴 DEMO 4: Priya Menon — Stroke Emergency (Emergency Path)

> *"Priya is 34, has a history of migraines. She gets headaches all the time. But today it's different."*

**Type this message:**
```
My face is drooping on one side and my speech is slurred. This headache is different from my usual migraines.
```

> *"Instant emergency response. The Steward detected stroke symptoms — face drooping and slurred speech. Even though Priya has a migraine history, the system correctly identifies this as a medical emergency.**
>
> *This is the difference between pattern matching and clinical triage. A simple keyword search might see 'headache' and route to neurology. DocSync sees 'face drooping' and calls an ambulance."*

---

### 🟢 DEMO 5: Arjun Nair — The New Patient (First Visit Flow)

> *"Arjun is 19, a college student. No medical history, no allergies, no medications. He's never used DocSync before."*

**Type this message:**
```
Hi, I've had a fever and sore throat for 2 days. My friend just tested positive for COVID. I'm worried.
```

**Point out:**
> *"Notice the sidebar shows empty medical history — this is a brand new patient. The system still works perfectly:*
> - *Extracts symptoms: fever*
> - *Notes the COVID exposure context*
> - *Generates a FHIR report with no prior history*
> - *Finds available doctors*
>
> *And after this consultation, Arjun now has a record in our system. His next visit loads this history automatically."*

---

### 🟢 DEMO 6: Ananya Iyer — Asthma Exacerbation (Edge Case)

> *"Ananya is 28, a software engineer with asthma since childhood. She's also anemic. She recently moved near a construction site."*

**Type this message:**
```
I'm having trouble breathing after being exposed to construction dust near my apartment. My inhaler isn't helping much.
```

> *"Watch what happens here — 'difficulty breathing' could trigger an emergency OR be a normal asthma flare. The Steward makes the call based on context. Either way, the system responds appropriately."*

---

## 🎤 PART 5: TECH DEEP-DIVE (60 seconds)

> *"Under the hood:*
>
> - **LangGraph** for stateful, cyclic pipeline orchestration — not a single chain, a real state machine with conditional routing
> - **MiniMax m2.7** for clinical reasoning — it receives the full patient context: symptoms, history, medications, allergies
> - **FHIR R4** for interoperability — every report is a real DiagnosticReport that plugs into any hospital EMR
> - **ABDM UHI** integration for doctor discovery and booking — India's national health stack
> - **SQLite persistence** with automatic seeding — patient data persists across sessions
> - **FastAPI** serving both the API and the chat interface — zero infrastructure beyond Python
>
> *The entire system starts in under 2 seconds, seeds the database automatically, and requires no external database server."*

---

## 🎤 PART 6: THE CLOSE (30 seconds)

> *"In India, 70% of healthcare spending is out-of-pocket. Patients don't have the luxury of wrong referrals. DocSync ensures:*
>
> - *The right urgency — emergencies in under 1 second, routine cases with full analysis*
> - *The right context — no lost allergies, no missed medications*
> - *The right doctor — matched to the diagnosis, not a random assignment*
> - *The right format — FHIR reports that travel with the patient"*
>
> ***"DocSync doesn't replace doctors. It gives doctors superpowers."***
>
> *Thank you.*

---

## 📋 JUDGE Q&A CHEAT SHEET

| Question | Answer |
|----------|--------|
| **How accurate is the diagnosis?** | It's not a diagnosis — it's a differential with confidence scoring. The doctor makes the final call. The FHIR report is a structured handoff, not a prescription. |
| **What if the LLM hallucinates?** | Three safeguards: (1) Steward node catches emergencies before the LLM runs, (2) Confidence scoring flags low-certainty results, (3) Diagnostic Gap pattern asks the patient follow-up questions when confidence is below 80%. |
| **Why LangGraph, not a simple chain?** | Clinical workflows have cycles — if confidence is low, we loop back and ask the patient for more info. Chains can't do that. LangGraph gives us conditional edges and state persistence. |
| **Can this handle multiple languages?** | The architecture supports it — the MiniMax model handles Hindi, and the symptom extraction is keyword-based. Full multilingual support (Kannada, Tamil) is in our Phase 7 roadmap. |
| **HIPAA/data privacy?** | No PII reaches logs. Patient data stays in the local SQLite DB. In production, we'd use encrypted PostgreSQL with row-level security. The FHIR reports use patient references, not names. |
| **What about real UHI integration?** | We have the full async UHI client with retry logic built. Currently using mock data because ABDM sandbox access takes 2-4 weeks. The code is production-ready — just needs API credentials. |
| **Cost to run?** | MiniMax m2.7 is ~$0.001 per consultation. At 1000 consultations/day, that's $30/month. The entire stack runs on a $5 VPS. |
| **What's the response time?** | Emergency path: <1 second. Normal path: 15-25 seconds (dominated by the LLM call). We show a typing indicator so the patient knows it's working. |

---

## 🎯 DEMO QUICK REFERENCE

Start server:
```bash
cd /home/syed/AI-Ignite/AI-Ignite-DocSync-Agent
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Open: **http://localhost:8000/chat**

| # | Patient | Phone | Message to Type |
|---|---------|-------|----------------|
| 1 | Ravi (Diabetes+BP) | +919876543210 | I have been having a persistent headache for the past 3 days, along with blurred vision |
| 2 | Farhan (Heart) | +919876543212 | I'm having severe chest tightness and sweating. Pain radiating to my left arm |
| 3 | Lakshmi (Multi-drug) | +919876543213 | My knee pain is extremely bad today. Both knees are swollen and I feel exhausted |
| 4 | Priya (Migraines) | +919876543215 | My face is drooping on one side and my speech is slurred |
| 5 | Arjun (New patient) | +919876543214 | Hi, I've had a fever and sore throat for 2 days. My friend tested positive for COVID |
| 6 | Ananya (Asthma) | +919876543211 | I'm having trouble breathing after being exposed to construction dust |

**Tip:** For the demo, show Demos 1, 2, and 5 at minimum (normal flow, emergency, new patient). Add others if time permits.
