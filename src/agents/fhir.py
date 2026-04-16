"""
FHIR Node - FHIR DiagnosticReport Generation

Generates FHIR R4 compliant DiagnosticReports from clinical findings.
"""
from datetime import datetime
from src.graph.state import PatientState
from src.fhir.generators import create_diagnostic_report


def fhir_node(state: PatientState) -> PatientState:
    """
    Generate FHIR DiagnosticReport from clinical findings.
    
    Args:
        state: Current patient state with clinical_findings and patient info
        
    Returns:
        Updated state with fhir_report populated
    """
    if not state.clinical_findings:
        state.error_message = "No clinical findings to report"
        return state
    
    report = create_diagnostic_report(
        patient_id=state.patient_id or state.phone_number,
        observations=state.clinical_findings,
        symptoms=state.symptoms,
        session_id=state.session_id,
        generated_at=datetime.utcnow()
    )
    
    state.fhir_report = report
    return state
