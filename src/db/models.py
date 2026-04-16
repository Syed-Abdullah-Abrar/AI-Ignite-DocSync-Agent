"""
Database Models - Patient Data

SQLAlchemy models for patient records and clinical data.
Optimized with proper indexes for query performance.
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, Index, Float, ForeignKey
from sqlalchemy import CheckConstraint
from datetime import datetime
from src.db.connection import Base


class Patient(Base):
    """Patient record model."""
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Medical data (JSON for flexibility)
    medical_history = Column(JSON, default=list)
    allergies = Column(JSON, default=list)
    current_medications = Column(JSON, default=list)
    
    # Table constraints
    __table_args__ = (
        CheckConstraint('length(phone_number) >= 10', name='phone_number_min_length'),
    )


class Session(Base):
    """Patient session/consultation record."""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Session data
    raw_message = Column(Text)
    symptoms = Column(JSON, default=list)
    symptom_duration = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    
    # Clinical reasoning
    clinical_findings = Column(JSON, default=list)
    # FIX: Changed from String to Float for proper numeric storage
    confidence_score = Column(Float, nullable=True)
    
    # FHIR report reference
    fhir_report_id = Column(String, nullable=True)
    
    # Booking
    appointment_id = Column(String, nullable=True)
    booking_confirmed = Column(Boolean, default=False)
    
    # Table indexes for performance
    __table_args__ = (
        # Composite index for querying sessions by patient with recent first
        Index('idx_sessions_patient_created', 'patient_id', 'created_at'),
        # Index for booking lookups
        Index('idx_sessions_appointment', 'appointment_id'),
    )


class Appointment(Base):
    """Appointment booking record."""
    __tablename__ = "appointments"
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"), index=True)
    doctor_id = Column(String, index=True)
    
    # Timing
    requested_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    
    # Details
    doctor_name = Column(String)
    hospital = Column(String)
    status = Column(String, default="pending")  # pending, confirmed, cancelled
    fhir_report_id = Column(String, nullable=True)
    
    # Table indexes for performance
    __table_args__ = (
        # Index for status filtering (common query pattern)
        Index('idx_appointments_status', 'status'),
        # Composite index for patient's appointments by time
        Index('idx_appointments_patient_status', 'patient_id', 'status', 'requested_at'),
        # Check constraint for valid status
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled', 'completed')",
            name='valid_appointment_status'
        ),
    )
