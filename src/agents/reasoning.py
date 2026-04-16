"""
Reasoning Node - Clinical Diagnostic Reasoning

Uses MiniMax m2.7 for clinical reasoning with Diagnostic Gap pattern.
Includes proper error handling and structured output support.
"""
from typing import Literal, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain.callbacks.tracers.langfuse import LangfuseTracer
from src.graph.state import PatientState
from src.config import config

logger = logging.getLogger(__name__)

# Initialize LLM with config
llm = ChatOpenAI(
    api_key=config.ai.minimax_api_key,
    base_url=config.ai.minimax_api_base,
    model=config.ai.model_name,
    temperature=0.3,
    max_retries=2,
    request_timeout=30
)


SYSTEM_PROMPT = """You are a clinical reasoning assistant. Given patient symptoms, 
medical history, and clinical findings, identify potential diagnoses and determine 
if additional information is needed.

Confidence threshold: 0.8 (80%)

Output format - respond with JSON:
{
  "findings": [{"description": "...", "code": "..."}],
  "confidence": 0.75,
  "gaps": ["question to ask patient?"]
}
"""


def reasoning_node(state: PatientState) -> PatientState:
    """
    Perform clinical reasoning using MiniMax m2.7.
    
    Args:
        state: Current patient state with symptoms and history
        
    Returns:
        Updated state with clinical_findings, confidence_score, diagnostic_gaps
    """
    if state.has_red_flags:
        return state  # Skip reasoning for emergencies
    
    prompt = build_clinical_prompt(state)
    
    try:
        response = llm.invoke(prompt)
        parsed = parse_clinical_response(response.content)
        
        state.clinical_findings = parsed.get("findings", [])
        state.confidence_score = parsed.get("confidence", 0.0)
        state.diagnostic_gaps = parsed.get("gaps", [])
        
        logger.info(f"Reasoning complete: confidence={state.confidence_score}")
        
    except Exception as e:
        logger.error(f"Reasoning failed: {e}")
        state.error_message = f"Clinical reasoning unavailable: {str(e)}"
        # Set default values to allow pipeline to continue
        state.clinical_findings = [{"description": "Unable to generate findings", "code": "ERROR"}]
        state.confidence_score = 0.0
        state.diagnostic_gaps = ["Unable to assess - please consult a doctor"]
    
    return state


def build_clinical_prompt(state: PatientState) -> str:
    """Build the clinical reasoning prompt from state."""
    prompt = f"""Patient Symptoms: {', '.join(state.symptoms)}
Duration: {state.symptom_duration or 'Not specified'}
Severity: {state.severity or 'Unknown'}

Medical History:
{format_history(state.medical_history)}

Allergies: {', '.join(state.allergies) if state.allergies else 'None known'}
Current Medications: {', '.join(state.current_medications) if state.current_medications else 'None'}

Provide clinical reasoning in JSON format."""
    return prompt


def format_history(history: list) -> str:
    """Format medical history for prompt."""
    if not history:
        return "No significant medical history"
    return "\n".join([
        f"- {h.get('condition', 'Unknown')}: {h.get('status', 'unknown')}"
        for h in history
    ])


def parse_clinical_response(response: str) -> dict:
    """
    Parse LLM response into structured findings.
    
    Attempts JSON parsing first, falls back to basic text extraction.
    """
    import json
    import re
    
    # Try JSON parsing first
    try:
        # Find JSON object in response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "findings": data.get("findings", [{"description": response}]),
                "confidence": float(data.get("confidence", 0.5)),
                "gaps": data.get("gaps", [])
            }
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"JSON parse failed, using fallback: {e}")
    
    # Fallback: extract basic information from text
    confidence = 0.5
    if "?" in response and ("uncertain" in response.lower() or "more information" in response.lower()):
        gaps = ["Additional history needed"]
        confidence = 0.6
    else:
        gaps = []
        confidence = 0.75
    
    return {
        "findings": [{"description": response}],
        "confidence": confidence,
        "gaps": gaps
    }


def ask_patient_node(state: PatientState) -> PatientState:
    """
    Ask patient for missing diagnostic information.
    
    Args:
        state: Current patient state with diagnostic_gaps
        
    Returns:
        Updated state - patient will provide answers in next message
    """
    # This node generates the question to ask the patient
    # The actual response will come through WhatsApp in a new session
    gap_questions = {
        "duration": "How long have you experienced these symptoms?",
        "severity": "On a scale of 1-10, how severe is your discomfort?",
        "additional": "Is there anything else you'd like to mention about your symptoms?"
    }
    
    # In production: send WhatsApp message with gap question
    logger.info(f"Asking patient for diagnostic gaps: {state.diagnostic_gaps}")
    
    return state
