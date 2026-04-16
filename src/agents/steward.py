"""
Steward Node - Safety Gate

Intercepts patient messages and detects medical red flags (emergencies).
"""
from typing import Literal
from langchain_core.messages import HumanMessage
from src.graph.state import PatientState


# Red flag keywords and patterns
RED_FLAG_PATTERNS = {
    "chest_pain": [
        "chest pain", "chest pressure", "chest tightness",
        "arm pain", "jaw pain", "left arm numbness"
    ],
    "stroke": [
        "stroke", "face drooping", "slurred speech",
        "numbness on one side", "confusion", "vision loss"
    ],
    "breathing": [
        "difficulty breathing", "shortness of breath",
        "can't breathe", "choking", "wheezing"
    ],
    "bleeding": [
        "severe bleeding", "blood in stool", "blood in vomit",
        "coughing blood"
    ],
    "consciousness": [
        "unconscious", "fainted", "lost consciousness",
        "seizure", "convulsions"
    ]
}


def steward_node(state: PatientState) -> PatientState:
    """
    Scan patient message for red flags.
    
    Args:
        state: Current patient state with raw_message
        
    Returns:
        Updated state with has_red_flags and red_flag_types set
    """
    message = state.raw_message.lower()
    
    detected_flags = []
    for flag_type, patterns in RED_FLAG_PATTERNS.items():
        for pattern in patterns:
            if pattern in message:
                detected_flags.append(flag_type)
                break
    
    state.has_red_flags = len(detected_flags) > 0
    state.red_flag_types = detected_flags
    
    return state


def emergency_node(state: PatientState) -> PatientState:
    """
    Handle emergency routing - contact emergency services.
    
    Args:
        state: Current patient state with red flags detected
        
    Returns:
        Updated state with error handling for emergency
    """
    # Log emergency for monitoring
    print(f"🚨 EMERGENCY DETECTED: {state.red_flag_types}")
    print(f"   Patient: {state.phone_number}")
    print(f"   Message: {state.raw_message}")
    
    # In production, this would:
    # 1. Send immediate WhatsApp response with emergency instructions
    # 2. Alert on-call medical staff
    # 3. Potentially contact emergency services
    
    state.error_message = (
        f"Emergency flags detected: {', '.join(state.red_flag_types)}. "
        "Please call emergency services immediately."
    )
    
    return state
