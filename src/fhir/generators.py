"""
FHIR Generators - FHIR R4 Resource Builders

Creates FHIR-compliant DiagnosticReport with full patient context:
- Chief complaints (symptoms)
- Clinical observations (LLM findings)
- Medical history (conditions)
- Allergies (AllergyIntolerance references)
- Current medications (MedicationStatement references)
"""
from datetime import datetime, timezone
from typing import Optional
import uuid


def create_diagnostic_report(
    patient_id: str,
    observations: list[dict],
    symptoms: list[str],
    session_id: str,
    generated_at: datetime,
    severity: Optional[str] = None,
    medical_history: Optional[list] = None,
    allergies: Optional[list] = None,
    current_medications: Optional[list] = None,
) -> dict:
    """
    Create a comprehensive FHIR DiagnosticReport from the pipeline state.
    
    This report gives the doctor a complete picture:
    - What the patient is experiencing NOW (symptoms + observations)
    - What the patient has HISTORICALLY (conditions, allergies, medications)
    - AI confidence and analysis (clinical findings)
    
    Args:
        patient_id: Patient identifier
        observations: Clinical observations/findings from the LLM
        symptoms: Extracted symptoms list
        session_id: Session identifier
        generated_at: Report generation timestamp
        severity: Overall severity (mild/moderate/severe)
        medical_history: Patient's past conditions
        allergies: Patient's known allergies
        current_medications: Patient's current medications
        
    Returns:
        FHIR DiagnosticReport as dict (JSON-serializable)
    """
    report_id = session_id or str(uuid.uuid4())[:8]
    
    # ── 1. Build Symptom Observations ──
    contained = []
    result_refs = []
    
    for i, symptom in enumerate(symptoms or []):
        obs_id = f"symptom-{i+1}"
        contained.append({
            "resourceType": "Observation",
            "id": obs_id,
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "exam",
                    "display": "Exam"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "418799008",
                    "display": "Symptom"
                }],
                "text": symptom.title()
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "valueString": symptom,
            "interpretation": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": _severity_code(severity),
                    "display": (severity or "unknown").title()
                }]
            }] if severity else []
        })
        result_refs.append({"reference": f"#{obs_id}"})
    
    # ── 2. Build Clinical Finding Observations (from LLM) ──
    for i, finding in enumerate(observations or []):
        obs_id = f"finding-{i+1}"
        contained.append({
            "resourceType": "Observation",
            "id": obs_id,
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "exam",
                    "display": "Exam"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "386661006",
                    "display": "Clinical finding"
                }],
                "text": finding.get("description", "Clinical observation")
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "valueString": finding.get("description", "")
        })
        result_refs.append({"reference": f"#{obs_id}"})
    
    # ── 3. Build Medical History Conditions ──
    conditions = []
    if medical_history:
        for i, condition in enumerate(medical_history):
            if isinstance(condition, dict):
                cond_id = f"condition-{i+1}"
                contained.append({
                    "resourceType": "Condition",
                    "id": cond_id,
                    "clinicalStatus": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": _map_condition_status(condition.get("status", "active"))
                        }]
                    },
                    "code": {
                        "text": condition.get("condition", "Unknown condition")
                    },
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "onsetDateTime": condition.get("diagnosed"),
                    "note": [{"text": condition.get("notes", "")}] if condition.get("notes") else []
                })
                conditions.append({"reference": f"#{cond_id}"})
    
    # ── 4. Build Allergy Resources ──
    allergy_resources = []
    if allergies:
        for i, allergy in enumerate(allergies):
            allergy_name = allergy if isinstance(allergy, str) else allergy.get("substance", "Unknown")
            allergy_id = f"allergy-{i+1}"
            contained.append({
                "resourceType": "AllergyIntolerance",
                "id": allergy_id,
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": "active"
                    }]
                },
                "type": "allergy",
                "code": {"text": allergy_name},
                "patient": {"reference": f"Patient/{patient_id}"}
            })
            allergy_resources.append({"reference": f"#{allergy_id}"})
    
    # ── 5. Build Medication Resources ──
    medication_resources = []
    if current_medications:
        for i, med in enumerate(current_medications):
            med_name = med if isinstance(med, str) else med.get("name", "Unknown")
            med_id = f"medication-{i+1}"
            contained.append({
                "resourceType": "MedicationStatement",
                "id": med_id,
                "status": "active",
                "medicationCodeableConcept": {"text": med_name},
                "subject": {"reference": f"Patient/{patient_id}"}
            })
            medication_resources.append({"reference": f"#{med_id}"})
    
    # ── 6. Assemble the DiagnosticReport ──
    report = {
        "resourceType": "DiagnosticReport",
        "id": f"report-{report_id}",
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/DiagnosticReport"],
            "lastUpdated": generated_at.isoformat()
        },
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://loinc.org",
                "code": "LP29684-5",
                "display": "Radiology"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "72198-7",
                "display": "Consultation note"
            }],
            "text": "DocSync AI Clinical Consultation Report"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": generated_at.isoformat(),
        "issued": generated_at.isoformat(),
        "contained": contained,
        "result": result_refs,
    }
    
    # ── 7. Add presentedForm — human-readable summary for the doctor ──
    summary_lines = [
        f"DocSync Clinical Consultation Report",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Patient: {patient_id}",
        f"",
        f"== CHIEF COMPLAINTS ==",
    ]
    for s in (symptoms or []):
        summary_lines.append(f"  • {s.title()}")
    if severity:
        summary_lines.append(f"  Severity: {severity.upper()}")
    
    summary_lines.append(f"")
    summary_lines.append(f"== CLINICAL FINDINGS ==")
    for obs in (observations or []):
        summary_lines.append(f"  • {obs.get('description', 'N/A')}")
    
    if medical_history:
        summary_lines.append(f"")
        summary_lines.append(f"== MEDICAL HISTORY ==")
        for h in medical_history:
            if isinstance(h, dict):
                status = h.get('status', 'active')
                summary_lines.append(f"  • {h.get('condition', 'N/A')} — {status} (since {h.get('diagnosed', 'unknown')})")
    
    if allergies:
        summary_lines.append(f"")
        summary_lines.append(f"== ALLERGIES ==")
        for a in allergies:
            name = a if isinstance(a, str) else a.get("substance", "Unknown")
            summary_lines.append(f"  ⚠ {name}")
    
    if current_medications:
        summary_lines.append(f"")
        summary_lines.append(f"== CURRENT MEDICATIONS ==")
        for m in current_medications:
            name = m if isinstance(m, str) else m.get("name", "Unknown")
            summary_lines.append(f"  💊 {name}")
    
    report["conclusion"] = "\n".join(summary_lines)
    
    return report


def _severity_code(severity: Optional[str]) -> str:
    """Map severity string to HL7 interpretation code."""
    mapping = {"mild": "L", "moderate": "N", "severe": "H", "critical": "HH"}
    return mapping.get((severity or "").lower(), "N")


def _map_condition_status(status: str) -> str:
    """Map patient history status to FHIR clinical status code."""
    mapping = {
        "active": "active",
        "managed": "active",
        "resolved": "resolved",
        "chronic": "active",
        "in_remission": "remission",
        "controlled": "active",
    }
    return mapping.get(status.lower(), "active")


def utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)
