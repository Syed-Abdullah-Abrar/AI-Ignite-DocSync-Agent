"""
FHIR Generators - FHIR R4 Resource Builders

Creates FHIR-compliant DiagnosticReport and related resources.
"""
from datetime import datetime, timezone
from typing import Optional


def create_diagnostic_report(
    patient_id: str,
    observations: list[dict],
    symptoms: list[str],
    session_id: str,
    generated_at: datetime
) -> dict:
    """
    Create a FHIR DiagnosticReport from clinical findings.
    
    Args:
        patient_id: Patient identifier
        observations: Clinical observations/findings
        symptoms: Extracted symptoms
        session_id: Session identifier
        generated_at: Report generation timestamp
        
    Returns:
        FHIR DiagnosticReport as dict (JSON-serializable)
    """
    # Build contained observations as proper FHIR resources
    contained = []
    for i, obs in enumerate(observations):
        contained.append({
            "resourceType": "Observation",
            "id": f"obs-{i+1}",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "386661006",
                    "display": "Clinical finding"
                }]
            },
            "valueString": obs.get("description", "")
        })
    
    # Create DiagnosticReport as a plain dict (FHIR-like format)
    # This avoids strict pydantic validation issues with fhir.resources
    report = {
        "resourceType": "DiagnosticReport",
        "id": f"report-{session_id}",
        "status": "final",
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "72198-7",
                "display": "Consultation note"
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "contained": contained,
        "effectiveDateTime": generated_at.isoformat()
    }
    
    return report


def create_symptom_observation(symptom: str, severity: str, duration: Optional[str] = None) -> dict:
    """
    Create a FHIR Observation for a symptom.
    
    Args:
        symptom: Symptom name
        severity: Symptom severity (mild/moderate/severe)
        duration: Optional duration string
        
    Returns:
        FHIR Observation as dict
    """
    interpretation_map = {
        "mild": "N",
        "moderate": "M", 
        "severe": "H"
    }
    
    observation = {
        "resourceType": "Observation",
        "id": f"symptom-{symptom}",
        "status": "final",
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "271681006",
                "display": symptom.title()
            }]
        },
        "interpretation": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": interpretation_map.get(severity.lower(), "N"),
                "display": severity.upper()
            }]
        }]
    }
    
    if duration:
        observation["note"] = [{"text": f"Duration: {duration}"}]
    
    return observation


def utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)
