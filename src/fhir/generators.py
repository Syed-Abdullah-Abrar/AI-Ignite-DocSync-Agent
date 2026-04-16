"""
FHIR Generators - FHIR R4 Resource Builders

Creates FHIR-compliant DiagnosticReport and related resources.
"""
from datetime import datetime
from typing import Optional
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.observation import Observation
from fhir.resources.reference import Reference
from fhir.resources.identifier import Identifier


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
    # Create identifiers
    identifiers = [
        Identifier(
            system="https://docsync.hackathon/session",
            value=session_id
        )
    ]
    
    # Build observations
    fhir_observations = []
    for i, obs in enumerate(observations):
        observation = Observation(
            id=f"obs-{i+1}",
            status="final",
            code={
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "386661006",  # Clinical finding
                    "display": obs.get("description", "Clinical finding")
                }]
            },
            valueString=obs.get("description", "")
        )
        fhir_observations.append(observation)
    
    # Create DiagnosticReport
    report = DiagnosticReport(
        id=f"report-{session_id}",
        status="final",
        code={
            "coding": [{
                "system": "http://loinc.org",
                "code": "72198-7",
                "display": "Consultation note"
            }]
        },
        subject={
            "reference": f"Patient/{patient_id}"
        },
        contained=observations,
        generated=generated_at.isoformat()
    )
    
    return report.model_dump(mode="json")


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
    observation = Observation(
        id=f"symptom-{symptom}",
        status="final",
        code={
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "271681006",  # Finding symptom
                "display": symptom.title()
            }]
        },
        interpretation=[{
            "text": severity.upper()
        }],
        note=[{"text": f"Duration: {duration}"}] if duration else None
    )
    
    return observation.model_dump(mode="json")
