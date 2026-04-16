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


# Thread pool for running sync graph in async context
_executor = ThreadPoolExecutor(max_workers=4)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("DocSync API starting up...")
    yield
    logger.info("DocSync API shutting down...")
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
    
    body = await request.json()
    
    message = body.get("message", "")
    phone = body.get("phone", "web-user")
    session_id = body.get("session_id")
    
    if not message:
        return {"error": "No message provided"}
    
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
        "medical_history": result.get("medical_history", []),
    }
    
    if has_red_flags:
        response["message"] = error_message
    elif booking_confirmed:
        response["message"] = f"Appointment booked! ID: {appointment_id}"
    elif clinical_findings:
        symptom_text = ', '.join(symptoms) if symptoms else 'your symptoms'
        response["message"] = f"I understand you're experiencing {symptom_text}. Here are available doctors near you."
    else:
        response["message"] = "Thank you for your message. How can I help you today?"
    
    return response


@app.get("/")
async def root():
    """Root endpoint — redirect to chat UI."""
    return FileResponse(os.path.join(CHAT_UI_DIR, "index.html"))


@app.get("/chat")
async def chat_page():
    """Serve the chat UI."""
    return FileResponse(os.path.join(CHAT_UI_DIR, "index.html"))


# Mount static assets for the chat UI (CSS, JS, images)
if os.path.isdir(CHAT_UI_DIR):
    app.mount("/static", StaticFiles(directory=CHAT_UI_DIR), name="chat-static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
