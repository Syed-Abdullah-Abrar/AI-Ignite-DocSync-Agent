"""
API Schemas - Pydantic Request/Response Models

Defines request/response schemas for FastAPI endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SymptomRequest(BaseModel):
    """Patient symptom submission via WhatsApp."""
    phone_number: str = Field(..., description="Patient phone number")
    message: str = Field(..., description="Raw patient message")
    session_id: Optional[str] = None


class SymptomResponse(BaseModel):
    """Acknowledgment of symptom intake."""
    status: str
    extracted_symptoms: list[str]
    questions: Optional[list[str]] = None


class AppointmentRequest(BaseModel):
    """Request to book an appointment."""
    patient_id: str
    doctor_id: str
    fhir_report_id: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Appointment booking response."""
    appointment_id: str
    doctor_name: str
    hospital: str
    appointment_time: datetime
    status: str


class HealthCheckResponse(BaseModel):
    """Health check endpoint response."""
    status: str
    version: str = "1.0.0"
    timestamp: datetime
