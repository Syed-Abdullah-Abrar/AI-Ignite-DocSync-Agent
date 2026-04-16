"""
DocSync State Machine

LangGraph StateGraph definition with clinical reasoning workflow.
"""
from typing import Annotated, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END


class PatientState(BaseModel):
    """State carried through the LangGraph pipeline."""
    
    # Patient identification
    patient_id: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Raw input
    raw_message: str = ""
    
    # Clinical data collected
    symptoms: list[str] = Field(default_factory=list)
    symptom_duration: Optional[str] = None
    severity: Optional[str] = None
    
    # Red flag detection
    has_red_flags: bool = False
    red_flag_types: list[str] = Field(default_factory=list)
    
    # Historical context
    medical_history: list[dict] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    
    # Diagnostic reasoning
    clinical_findings: list[dict] = Field(default_factory=list)
    confidence_score: float = 0.0
    diagnostic_gaps: list[str] = Field(default_factory=list)
    
    # FHIR output
    fhir_report: Optional[dict] = None
    
    # UHI booking
    doctor_options: list[dict] = Field(default_factory=list)
    selected_doctor: Optional[dict] = None
    appointment_id: Optional[str] = None
    booking_confirmed: bool = False
    
    # Error handling
    error_message: Optional[str] = None
    
    # Metadata
    session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


def create_graph():
    """Create and compile the DocSync StateGraph."""
    builder = StateGraph(PatientState)
    
    # Add nodes
    builder.add_node("steward", "steward_node")
    builder.add_node("symptom", "symptom_node")
    builder.add_node("history", "history_node")
    builder.add_node("reasoning", "reasoning_node")
    builder.add_node("ask_patient", "ask_patient_node")
    builder.add_node("fhir", "fhir_node")
    builder.add_node("uhi_discovery", "uhi_discovery_node")
    builder.add_node("uhi_confirm", "uhi_confirm_node")
    builder.add_node("emergency", "emergency_node")
    builder.add_node("notify_patient", "notify_patient_node")
    
    # Define routing logic
    def route_after_steward(state: PatientState) -> str:
        """Route after steward node based on red flags."""
        if state.has_red_flags:
            return "emergency"
        return "symptom"
    
    def route_after_reasoning(state: PatientState) -> str:
        """Route after reasoning based on confidence."""
        if state.confidence_score < 0.8 and state.diagnostic_gaps:
            return "ask_patient"
        return "fhir"
    
    def route_after_uhi_discovery(state: PatientState) -> str:
        """Route after UHI discovery."""
        if state.selected_doctor:
            return "uhi_confirm"
        return END
    
    # Set entry point and edges
    builder.set_entry_point("steward")
    
    # Sequential edges
    builder.add_edge("symptom", "history")
    builder.add_edge("history", "reasoning")
    builder.add_edge("ask_patient", "reasoning")  # Loop back for more info
    builder.add_edge("reasoning", "fhir")
    builder.add_edge("fhir", "uhi_discovery")
    builder.add_edge("uhi_confirm", "notify_patient")
    builder.add_edge("notify_patient", END)
    
    # Emergency routing - CRITICAL FIX: added edge to END
    builder.add_edge("emergency", END)
    
    # Conditional edges
    builder.add_conditional_edges("steward", route_after_steward)
    builder.add_conditional_edges("reasoning", route_after_reasoning)
    builder.add_conditional_edges("uhi_discovery", route_after_uhi_discovery)
    
    return builder.compile()


# Singleton graph instance
_graph = None

def get_graph():
    """Get the compiled graph instance."""
    global _graph
    if _graph is None:
        _graph = create_graph()
    return _graph
