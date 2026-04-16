"""
Symptom Node - Symptom Intake

Extracts structured symptom data from natural language patient input.
"""
from typing import Optional
from src.graph.state import PatientState


# Common symptom keywords for extraction
SYMPTOM_KEYWORDS = {
    "headache": ["headache", "head pain", "head ache"],
    "fever": ["fever", "high temperature", "febrile"],
    "cough": ["cough", "coughing"],
    "fatigue": ["tired", "fatigue", "exhausted", "weakness"],
    "nausea": ["nausea", "nauseous", "sick to stomach"],
    "pain": ["pain", "ache", "soreness"],
    "dizziness": ["dizziness", "dizzy", "lightheaded"],
    "abdominal": ["stomach pain", "abdominal pain", "belly pain"]
}

DURATION_PATTERNS = [
    (r"(\d+)\s*day", "days"),
    (r"(\d+)\s*week", "weeks"),
    (r"(\d+)\s*month", "months"),
    (r"since\s+(\w+)", "since")
]

SEVERITY_PATTERNS = {
    "mild": ["mild", "slight", "minor"],
    "moderate": ["moderate", "medium"],
    "severe": ["severe", "intense", "worst", "extreme"]
}


def symptom_node(state: PatientState) -> PatientState:
    """
    Extract structured symptoms from raw patient message.
    
    Args:
        state: Current patient state with raw_message
        
    Returns:
        Updated state with symptoms, duration, and severity
    """
    message = state.raw_message.lower()
    
    # Extract symptoms
    detected_symptoms = []
    for symptom, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message:
                detected_symptoms.append(symptom)
                break
    
    state.symptoms = detected_symptoms
    
    # Extract duration
    duration = extract_duration(message)
    state.symptom_duration = duration
    
    # Extract severity
    severity = extract_severity(message)
    state.severity = severity
    
    return state


def extract_duration(message: str) -> Optional[str]:
    """Extract symptom duration from message."""
    import re
    for pattern, unit in DURATION_PATTERNS:
        match = re.search(pattern, message)
        if match:
            value = match.group(1)
            return f"{value} {unit}"
    return None


def extract_severity(message: str) -> Optional[str]:
    """Extract symptom severity from message."""
    for severity, keywords in SEVERITY_PATTERNS.items():
        for keyword in keywords:
            if keyword in message:
                return severity
    return "mild"  # Default assumption
