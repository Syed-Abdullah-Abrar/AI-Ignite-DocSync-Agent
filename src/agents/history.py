"""
History Node - Patient Medical History

Retrieves longitudinal patient records from PostgreSQL.
"""
from typing import Optional
from src.graph.state import PatientState


def history_node(state: PatientState) -> PatientState:
    """
    Retrieve patient history from database.
    
    Args:
        state: Current patient state with patient_id or phone_number
        
    Returns:
        Updated state with medical_history, allergies, current_medications
    """
    if not state.patient_id and not state.phone_number:
        # New patient - initialize empty history
        state.medical_history = []
        state.allergies = []
        state.current_medications = []
        return state
    
    # In production, query PostgreSQL:
    # patient = db.patients.find_one(phone=state.phone_number)
    # state.medical_history = patient.get("conditions", [])
    # state.allergies = patient.get("allergies", [])
    # state.current_medications = patient.get("medications", [])
    
    # Mock data for development
    state.medical_history = [
        {"condition": "Type 2 Diabetes", "diagnosed": "2022-03-15", "status": "managed"},
        {"condition": "Hypertension", "diagnosed": "2021-08-01", "status": "managed"}
    ]
    state.allergies = ["Penicillin"]
    state.current_medications = ["Metformin 500mg", "Lisinopril 10mg"]
    
    return state


def update_patient_history(state: PatientState, new_condition: dict) -> PatientState:
    """
    Update patient history with new clinical data.
    
    Args:
        state: Current patient state
        new_condition: Condition dict with type, date, notes
        
    Returns:
        Updated state with appended history
    """
    if state.patient_id:
        state.medical_history.append(new_condition)
    return state
