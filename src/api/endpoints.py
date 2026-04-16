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


# Mock doctors (UHI doctors are not yet in the DB)
MOCK_DOCTORS = [
    {"id": "d1", "name": "Dr. Sharma", "specialty": "General Physician", "available": True, "hospital": "Manipal Hospital", "distance": "2.3 km"},
    {"id": "d2", "name": "Dr. Kumar", "specialty": "Internal Medicine", "available": True, "hospital": "Apollo Hospitals", "distance": "4.1 km"},
    {"id": "d3", "name": "Dr. Reddy", "specialty": "Pulmonology", "available": False, "hospital": "Narayana Health", "distance": "5.5 km"},
]


async def _get_db_session():
    """Get async database session."""
    from src.db.connection import get_session_factory
    factory = get_session_factory()
    async with factory() as session:
        yield session


def _patient_to_response(patient) -> dict:
    """Convert Patient model to API response format."""
    # Map patient record to dashboard format
    # Use phone_number as unique identifier, derive status from history
    return {
        "id": patient.id,
        "name": patient.name or f"Patient {patient.id[-4:]}",
        "status": "symptoms_detected",  # Default - could be derived from sessions
        "severity": "mild",  # Default - could be derived from sessions
        "phone_number": patient.phone_number,
    }


@router.get("/patients", response_model=list[PatientResponse])
async def get_patients():
    """
    Get all patients for the 3D dashboard.
    
    Queries the database for all patients.
    """
    from sqlalchemy import select
    from src.db.connection import get_engine
    from src.db.models import Patient
    
    engine = get_engine()
    async with engine.begin() as conn:
        result = await conn.execute(select(Patient))
        patients = result.scalars().all()
    
    return [_patient_to_response(p) for p in patients]


@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str):
    """Get a specific patient by ID."""
    from sqlalchemy import select
    from src.db.connection import get_engine
    from src.db.models import Patient
    
    engine = get_engine()
    async with engine.begin() as conn:
        result = await conn.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return _patient_to_response(patient)


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
    
    Returns counts for active patients, sessions, and available doctors.
    """
    from sqlalchemy import select, func
    from src.db.connection import get_engine
    from src.db.models import Patient, Session, Appointment
    
    engine = get_engine()
    async with engine.begin() as conn:
        # Count patients
        patients_count = await conn.execute(select(func.count(Patient.id)))
        active_patients = patients_count.scalar() or 0
        
        # Count sessions (rough proxy for active reasoning)
        sessions_count = await conn.execute(select(func.count(Session.id)))
        in_reasoning = min(sessions_count.scalar() or 0, active_patients)
        
        # Count confirmed appointments
        appointments_count = await conn.execute(
            select(func.count(Appointment.id)).where(Appointment.status == "confirmed")
        )
        booking_confirmed = appointments_count.scalar() or 0
        
        # Count available doctors (from mock)
        available = len([d for d in MOCK_DOCTORS if d["available"]])
    
    return DashboardStatsResponse(
        active_patients=active_patients,
        in_reasoning=in_reasoning,
        booking_confirmed=booking_confirmed,
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
    import uuid
    import asyncio
    from sqlalchemy import select
    from src.db.connection import get_engine
    from src.db.models import Patient, Appointment
    
    engine = get_engine()
    
    # Validate patient exists
    async with engine.begin() as conn:
        result = await conn.execute(select(Patient).where(Patient.id == request.patient_id))
        patient = result.scalar_one_or_none()
    
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
    
    # Create appointment record in database
    appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
    
    async with engine.begin() as conn:
        appointment = Appointment(
            id=appointment_id,
            patient_id=request.patient_id,
            doctor_id=request.doctor_id,
            doctor_name=doctor["name"],
            hospital=doctor.get("hospital", ""),
            status="confirmed",
            confirmed_at=datetime.utcnow(),
        )
        conn.add(appointment)
    
    return BookingResponse(
        success=True,
        appointment_id=appointment_id,
        message=f"Appointment booked with {doctor['name']} at {doctor['hospital']}"
    )
