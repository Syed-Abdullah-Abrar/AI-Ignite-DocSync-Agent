"""
History Node - Patient Medical History

Retrieves longitudinal patient records from data/patients.json.
"""
import json
import os
from src.graph.state import PatientState


def _load_patients() -> list[dict]:
    """Load patients from data/patients.json."""
    # Lazy import to avoid circular issues
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    patients_path = os.path.join(project_root, "data", "patients.json")
    
    with open(patients_path, "r") as f:
        data = json.load(f)
    
    return data.get("patients", [])


def _find_patient(phone_number: str, patient_id: str | None) -> dict | None:
    """Find patient by phone_number or patient_id."""
    patients = _load_patients()
    
    # Try phone_number first (primary lookup)
    if phone_number:
        for patient in patients:
            if patient.get("phone_number") == phone_number:
                return patient
    
    # Fallback to patient_id
    if patient_id:
        for patient in patients:
            if patient.get("id") == patient_id:
                return patient
    
    return None


def history_node(state: PatientState) -> PatientState:
    """
    Retrieve patient history from data/patients.json.
    
    Args:
        state: Current patient state with patient_id or phone_number
        
    Returns:
        Updated state with medical_history, allergies, current_medications
    """
    patient = _find_patient(
        phone_number=state.phone_number,
        patient_id=state.patient_id
    )
    
    if patient:
        # Found patient — load their real data
        state.medical_history = patient.get("medical_history", [])
        state.allergies = patient.get("allergies", [])
        state.current_medications = patient.get("current_medications", [])
        # Store patient_id if not set (enables future DB lookups)
        if not state.patient_id:
            state.patient_id = patient.get("id")
    else:
        # New/unknown patient — initialize empty history
        state.medical_history = []
        state.allergies = []
        state.current_medications = []
    
    return state


def update_patient_history(state: PatientState, new_condition: dict) -> PatientState:
    """
    Update patient history with new clinical data.
    
    Note: This only updates the in-memory state. In production,
    persist to PostgreSQL via the db layer.
    
    Args:
        state: Current patient state
        new_condition: Condition dict with type, date, notes
        
    Returns:
        Updated state with appended history
    """
    if state.patient_id:
        state.medical_history.append(new_condition)
    return state
