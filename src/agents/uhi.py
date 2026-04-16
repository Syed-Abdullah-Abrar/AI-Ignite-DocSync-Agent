"""
UHI Node - ABDM UHI Integration

Doctor discovery and appointment booking via ABDM Unified Health Interface.
"""
import asyncio
from typing import Optional
from src.graph.state import PatientState
from src.api.uhi_client import UHIClient


def uhi_discovery_node(state: PatientState) -> PatientState:
    """
    Discover available doctors via UHI Gateway.
    
    Args:
        state: Current patient state with fhir_report and location
        
    Returns:
        Updated state with doctor_options
    """
    if not state.fhir_report:
        state.error_message = "No FHIR report available for doctor search"
        return state
    
    client = UHIClient()
    
    # Search based on symptoms and urgency
    search_params = {
        "symptoms": state.symptoms,
        "severity": state.severity,
        "location": "Bangalore"  # Default for hackathon
    }
    
    # Run async search - handle both Jupyter and standalone contexts
    try:
        # Check if there's already a running event loop (Jupyter)
        loop = asyncio.get_running_loop()
        # If we're in an event loop, create a task and use asyncio.run_forever trick
        # or just get the result directly
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, client.search_doctors(search_params))
            doctors = future.result()
    except RuntimeError:
        # No running event loop - use asyncio.run normally
        doctors = asyncio.run(client.search_doctors(search_params))
    
    state.doctor_options = doctors
    return state


def uhi_confirm_node(state: PatientState) -> PatientState:
    """
    Confirm appointment booking with selected doctor.
    
    Args:
        state: Current patient state with selected_doctor
        
    Returns:
        Updated state with appointment_id and booking_confirmed
    """
    if not state.selected_doctor:
        state.error_message = "No doctor selected for booking"
        return state
    
    client = UHIClient()
    
    # Run async confirm
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                client.confirm_appointment(
                    doctor=state.selected_doctor,
                    patient_id=state.patient_id or state.phone_number,
                    fhir_report=state.fhir_report
                )
            )
            booking = future.result()
    except RuntimeError:
        booking = asyncio.run(
            client.confirm_appointment(
                doctor=state.selected_doctor,
                patient_id=state.patient_id or state.phone_number,
                fhir_report=state.fhir_report
            )
        )
    
    state.appointment_id = booking.get("appointment_id")
    state.booking_confirmed = True
    
    return state


def notify_patient_node(state: PatientState) -> PatientState:
    """
    Send booking confirmation via WhatsApp.
    
    Args:
        state: Current patient state with booking details
        
    Returns:
        Updated state - notification sent
    """
    # In production: send WhatsApp notification with:
    # - Doctor name and specialty
    # - Appointment time
    # - Location/venue
    # - FHIR report summary
    print(f"📱 Booking confirmed for {state.phone_number}")
    print(f"   Doctor: {state.selected_doctor.get('name')}")
    print(f"   Appointment ID: {state.appointment_id}")
    
    return state
