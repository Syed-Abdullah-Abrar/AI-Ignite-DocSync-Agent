"""
DocSync API - FastAPI Application

Main entry point for the DocSync backend service.
"""
import os
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import logging

from src.api.callbacks import router as uhi_router
from src.api.endpoints import router as dashboard_router
from src.api.schemas import HealthCheckResponse
from src.graph.state import get_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to chat UI directory
CHAT_UI_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "chat")
DOCTOR_UI_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "doctor")


# Thread pool for running sync graph in async context
_executor = ThreadPoolExecutor(max_workers=4)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("DocSync API starting up...")
    
    # Initialize database tables
    from src.db.connection import init_db, seed_patients_if_empty, close_db
    await init_db()
    await seed_patients_if_empty()
    logger.info("Database initialized and seeded")
    
    yield
    logger.info("DocSync API shutting down...")
    await close_db()
    _executor.shutdown(wait=True)


app = FastAPI(
    title="DocSync API",
    description="Healthcare Coordination Agent - ABDM UHI Integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(uhi_router)
app.include_router(dashboard_router)


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc)
    )


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Receive WhatsApp messages via MCP webhook.
    
    This endpoint receives patient messages and orchestrates
    the LangGraph pipeline.
    """
    import asyncio
    
    body = await request.json()
    
    # Extract message data
    phone = body.get("from", "")
    message = body.get("text", "")
    session_id = body.get("session_id")
    
    # Initialize state
    from src.graph.state import PatientState
    state = PatientState(
        phone_number=phone,
        raw_message=message,
        session_id=session_id
    )
    
    # Run pipeline - use thread pool to avoid blocking
    graph = get_graph()
    
    # Run sync invoke in thread pool for async context
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        _executor,
        lambda: graph.invoke(state)
    )
    
    return {"status": "processed", "session_id": session_id}


@app.post("/chat/message")
async def chat_message(request: Request):
    """
    Receive chat messages via web interface.
    
    This endpoint receives patient messages from the web chat
    and orchestrates the LangGraph pipeline.
    """
    import asyncio
    import re
    
    body = await request.json()
    
    message = body.get("message", "")
    phone = body.get("phone", "web-user")
    session_id = body.get("session_id")
    
    if not message:
        return {"error": "No message provided"}
    
    # ── Conversational pre-filter ──
    # Detect greetings and non-medical messages to avoid running the full pipeline
    msg_lower = message.strip().lower()
    
    GREETINGS = {"hello", "hi", "hey", "good morning", "good evening", "good afternoon",
                 "what's up", "sup", "howdy", "namaste", "namaskar", "hola"}
    THANKS = {"thank you", "thanks", "thank u", "thx", "ty", "dhanyavaad", "shukriya"}
    HELP_WORDS = {"help", "what can you do", "how does this work", "what is this",
                  "who are you", "what are you"}
    
    if msg_lower in GREETINGS or any(msg_lower.startswith(g) for g in GREETINGS):
        return {
            "status": "greeting",
            "message": "Hello! 👋 I'm DocSync, your healthcare assistant. Please describe your symptoms and I'll help connect you with the right doctor.\n\nFor example: \"I have a headache for 3 days\" or \"I'm having chest pain\"",
            "symptoms": [], "severity": None, "has_red_flags": False,
            "booking_confirmed": False, "appointment_id": None,
            "doctor_options": [], "clinical_findings": [],
            "fhir_report": None, "confidence_score": 0, "medical_history": [],
        }
    
    if any(t in msg_lower for t in THANKS):
        return {
            "status": "thanks",
            "message": "You're welcome! 🙏 Take care of your health. If you experience any new symptoms, don't hesitate to reach out.",
            "symptoms": [], "severity": None, "has_red_flags": False,
            "booking_confirmed": False, "appointment_id": None,
            "doctor_options": [], "clinical_findings": [],
            "fhir_report": None, "confidence_score": 0, "medical_history": [],
        }
    
    if any(h in msg_lower for h in HELP_WORDS):
        return {
            "status": "help",
            "message": "I'm DocSync — an AI healthcare coordination agent. Here's what I can do:\n\n🔍 **Symptom Analysis** — Describe your symptoms and I'll extract and analyze them\n🏥 **Doctor Matching** — I'll find available specialists near you\n📋 **FHIR Reports** — I generate clinical reports that any hospital can read\n🚨 **Emergency Detection** — I instantly detect life-threatening symptoms\n\nTry describing how you're feeling!",
            "symptoms": [], "severity": None, "has_red_flags": False,
            "booking_confirmed": False, "appointment_id": None,
            "doctor_options": [], "clinical_findings": [],
            "fhir_report": None, "confidence_score": 0, "medical_history": [],
        }
    
    # ── Run the medical pipeline ──
    from src.graph.state import PatientState
    state = PatientState(
        phone_number=phone,
        raw_message=message,
        session_id=session_id
    )
    
    graph = get_graph()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        _executor,
        lambda: graph.invoke(state)
    )
    
    # LangGraph returns a dict with Pydantic v2
    symptoms = result.get("symptoms", [])
    severity = result.get("severity")
    has_red_flags = result.get("has_red_flags", False)
    booking_confirmed = result.get("booking_confirmed", False)
    appointment_id = result.get("appointment_id")
    clinical_findings = result.get("clinical_findings", [])
    error_message = result.get("error_message")
    doctor_options = result.get("doctor_options", [])
    fhir_report = result.get("fhir_report")
    medical_history = result.get("medical_history", [])
    
    response = {
        "status": "processed",
        "session_id": result.get("session_id"),
        "symptoms": symptoms,
        "severity": severity,
        "has_red_flags": has_red_flags,
        "booking_confirmed": booking_confirmed,
        "appointment_id": appointment_id,
        "doctor_options": doctor_options,
        "clinical_findings": clinical_findings,
        "fhir_report": fhir_report,
        "confidence_score": result.get("confidence_score", 0),
        "medical_history": medical_history,
    }
    
    # ── Build contextual response message ──
    if has_red_flags:
        response["message"] = error_message
    elif booking_confirmed:
        response["message"] = f"✅ Appointment booked! Your appointment ID is: {appointment_id}"
    elif symptoms and doctor_options:
        symptom_text = ', '.join(symptoms)
        severity_text = f" (severity: {severity})" if severity else ""
        history_text = ""
        if medical_history:
            conditions = [h.get("condition", "") for h in medical_history if isinstance(h, dict)]
            if conditions:
                history_text = f"\n\n📋 I found your medical records: {', '.join(conditions)}. This context has been considered in the analysis."
        response["message"] = (
            f"Based on your description, I've identified: **{symptom_text}**{severity_text}.\n\n"
            f"I've analyzed your symptoms and found {len(doctor_options)} available doctor(s) near you."
            f"{history_text}\n\n"
            f"👇 See the doctor cards below to book an appointment."
        )
    elif symptoms:
        symptom_text = ', '.join(symptoms)
        response["message"] = f"I've identified: **{symptom_text}**. Let me look into this further for you."
    else:
        response["message"] = (
            "I couldn't identify specific symptoms from your message. "
            "Could you describe what you're feeling in more detail?\n\n"
            "For example: \"I have a headache and fever for 2 days\" or \"My knee is swollen and painful\""
        )
    
    return response


from pydantic import BaseModel

class AppointmentAcceptRequest(BaseModel):
    patient_name: str
    phone_number: str
    doctor_name: str
    appointment_time: str

@app.post("/api/appointments/accept")
async def accept_appointment(req: AppointmentAcceptRequest):
    """Called by Doctor's Dashboard to accept appointment & trigger SMS."""
    from src.api.twilio_client import send_appointment_sms
    # Trigger Twilio SMS to the patient
    success = send_appointment_sms(
        phone_number=req.phone_number,
        patient_name=req.patient_name,
        doctor_name=req.doctor_name,
        appointment_time=req.appointment_time
    )
    return {"status": "confirmed", "sms_sent": success}

@app.get("/")
async def root():
    """Root endpoint — redirect to chat UI."""
    return FileResponse(os.path.join(CHAT_UI_DIR, "index.html"))


@app.get("/chat")
async def chat_page():
    """Serve the chat UI."""
    return FileResponse(os.path.join(CHAT_UI_DIR, "index.html"))


@app.get("/doctor")
async def doctor_page():
    """Serve the doctor EMR UI."""
    return FileResponse(os.path.join(DOCTOR_UI_DIR, "index.html"))


# Mount static assets for the chat UI (CSS, JS, images)
if os.path.isdir(CHAT_UI_DIR):
    app.mount("/static", StaticFiles(directory=CHAT_UI_DIR), name="chat-static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
