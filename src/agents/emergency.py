"""
Emergency Node - Emergency Routing

Handles red flag cases with immediate escalation.
"""
from src.graph.state import PatientState


def emergency_node(state: PatientState) -> PatientState:
    """
    Route emergency to appropriate services.
    
    Args:
        state: Current patient state with red_flags detected
        
    Returns:
        Updated state with emergency_handled flag
    """
    emergency_messages = {
        "chest_pain": "Please call emergency services (108) immediately. If in Bangalore, Fortis Emergency: 080-66214444",
        "stroke": "Please call emergency services (108) immediately. Remember FAST: Face, Arms, Speech, Time",
        "breathing": "Please call emergency services (108) immediately. Sit upright and try to stay calm.",
        "bleeding": "Please call emergency services (108) immediately. Apply pressure to bleeding site.",
        "consciousness": "Please call emergency services (108) immediately. Do not give food or water."
    }
    
    primary_flag = state.red_flag_types[0] if state.red_flag_types else "general"
    state.error_message = emergency_messages.get(
        primary_flag,
        "Please call emergency services immediately."
    )
    
    # In production:
    # 1. Send immediate WhatsApp response
    # 2. Alert on-call medical staff dashboard
    # 3. Log for compliance/audit
    
    return state
