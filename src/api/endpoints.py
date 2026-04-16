"""
API Endpoints - Patient & Doctor Data

FastAPI endpoints for fetching patient and doctor data for the 3D dashboard.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


router = APIRouter(prefix="/api", tags=["dashboard"])


class PatientResponse(BaseModel):
    """Patient data for dashboard."""
    id: str
    name: str
    status: str
    severity: str
    phone_number: Optional[str] = None


class DoctorResponse(BaseModel):
    """Doctor data for dashboard."""
    id: str
    name: str
    specialty: str
    available: bool
    hospital: Optional[str] = None
    distance: Optional[str] = None


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics."""
    active_patients: int
    in_reasoning: int
    booking_confirmed: int
    available_doctors: int


# Mock data for development - in production, this comes from PostgreSQL
MOCK_PATIENTS = [
    {"id": "1", "name": "Patient A", "status": "symptoms_detected", "severity": "moderate"},
    {"id": "2", "name": "Patient B", "status": "reasoning", "severity": "mild"},
    {"id": "3", "name": "Patient C", "status": "booking", "severity": "mild"},
    {"id": "4", "name": "Patient D", "status": "symptoms_detected", "severity": "severe"},
]

MOCK_DOCTORS = [
    {"id": "d1", "name": "Dr. Sharma", "specialty": "General Physician", "available": True, "hospital": "Manipal Hospital", "distance": "2.3 km"},
    {"id": "d2", "name": "Dr. Kumar", "specialty": "Internal Medicine", "available": True, "hospital": "Apollo Hospitals", "distance": "4.1 km"},
    {"id": "d3", "name": "Dr. Reddy", "specialty": "Pulmonology", "available": False, "hospital": "Narayana Health", "distance": "5.5 km"},
]


@router.get("/patients", response_model=list[PatientResponse])
async def get_patients():
    """
    Get all patients for the 3D dashboard.
    
    In production, this queries the database for active patient sessions.
    """
    return MOCK_PATIENTS


@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    """Get a specific patient by ID."""
    for patient in MOCK_PATIENTS:
        if patient["id"] == patient_id:
            return patient
    raise HTTPException(status_code=404, detail="Patient not found")


@router.get("/doctors", response_model=list[DoctorResponse])
async def get_doctors():
    """
    Get all available doctors for the 3D dashboard.
    
    In production, this comes from UHI discovery or cached doctor list.
    """
    return MOCK_DOCTORS


@router.get("/doctors/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: str):
    """Get a specific doctor by ID."""
    for doctor in MOCK_DOCTORS:
        if doctor["id"] == doctor_id:
            return doctor
    raise HTTPException(status_code=404, detail="Doctor not found")


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_stats():
    """
    Get dashboard statistics.
    
    Returns counts for active patients, in-reasoning, bookings, and available doctors.
    """
    active = len([p for p in MOCK_PATIENTS if p["status"] in ["symptoms_detected", "reasoning", "booking"]])
    reasoning = len([p for p in MOCK_PATIENTS if p["status"] == "reasoning"])
    booking = len([p for p in MOCK_PATIENTS if p["status"] == "booking"])
    available = len([d for d in MOCK_DOCTORS if d["available"]])
    
    return DashboardStatsResponse(
        active_patients=active,
        in_reasoning=reasoning,
        booking_confirmed=booking,
        available_doctors=available
    )


class BookingRequest(BaseModel):
    """Request to book a patient with a doctor."""
    patient_id: str
    doctor_id: str


class BookingResponse(BaseModel):
    """Booking confirmation response."""
    success: bool
    appointment_id: Optional[str] = None
    message: str


@router.post("/book", response_model=BookingResponse)
async def create_booking(request: BookingRequest):
    """
    Book an appointment between a patient and doctor.
    
    This triggers the UHI booking flow and returns confirmation.
    """
    # Validate patient exists
    patient = None
    for p in MOCK_PATIENTS:
        if p["id"] == request.patient_id:
            patient = p
            break
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Validate doctor exists and is available
    doctor = None
    for d in MOCK_DOCTORS:
        if d["id"] == request.doctor_id:
            doctor = d
            break
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    if not doctor["available"]:
        return BookingResponse(
            success=False,
            message=f"Doctor {doctor['name']} is not available"
        )
    
    # In production: call uhi_confirm_node via the graph pipeline
    # For now, return mock confirmation
    import uuid
    appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
    
    return BookingResponse(
        success=True,
        appointment_id=appointment_id,
        message=f"Appointment booked with {doctor['name']} at {doctor['hospital']}"
    )
