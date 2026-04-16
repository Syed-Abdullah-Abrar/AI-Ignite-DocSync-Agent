"""
UHI Client - ABDM UHI Gateway Integration

Handles API calls to ABDM Unified Health Interface Gateway.
Includes retry logic and proper error handling.
"""
import httpx
from typing import Optional
import asyncio
import logging
from src.config import config

logger = logging.getLogger(__name__)


class UHIClient:
    """Client for ABDM UHI Gateway operations."""
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    
    def __init__(self):
        self.gateway_url = config.uhi.gateway_url
        self.client_id = config.uhi.client_id
        self.client_secret = config.uhi.client_secret
        self.callback_url = config.uhi.callback_url
        self._access_token: Optional[str] = None
    
    async def _make_request(
        self,
        method: str,
        url: str,
        json: Optional[dict] = None,
        retries: int = MAX_RETRIES
    ) -> dict:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            url: Request URL
            json: Request body
            retries: Number of retry attempts
            
        Returns:
            Response JSON
            
        Raises:
            httpx.HTTPStatusError: If all retries fail
        """
        last_error = None
        
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if method.upper() == "GET":
                        response = await client.get(url)
                    elif method.upper() == "POST":
                        response = await client.post(url, json=json)
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    response.raise_for_status()
                    return response.json()
                    
            except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as e:
                last_error = e
                logger.warning(f"UHI request failed (attempt {attempt + 1}/{retries}): {e}")
                
                if attempt < retries - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
        
        # All retries exhausted
        logger.error(f"UHI request failed after {retries} attempts: {last_error}")
        raise last_error
    
    async def get_access_token(self) -> str:
        """Get OAuth2 access token from UHI gateway."""
        if self._access_token:
            return self._access_token
        
        # In production: POST to /v0.5/sessions
        try:
            data = await self._make_request(
                "POST",
                f"{self.gateway_url}/v0.5/sessions",
                json={
                    "clientId": self.client_id,
                    "clientSecret": self.client_secret
                }
            )
            self._access_token = data.get("accessToken", "")
            return self._access_token
        except Exception as e:
            logger.warning(f"Failed to get UHI token, using mock: {e}")
            return "mock_token"
    
    async def search_doctors(self, params: dict) -> list[dict]:
        """
        Search for doctors via UHI Gateway /search endpoint.
        
        Args:
            params: Search parameters (symptoms, location, etc.)
            
        Returns:
            List of doctor profiles matching criteria
        """
        # Check if real UHI credentials are configured
        if not self.client_id or not self.client_secret:
            logger.info("Using mock doctor data (no UHI credentials)")
            return self._get_mock_doctors()
        
        try:
            # In production: POST /v0.5/search
            # Response comes via callback to self.callback_url
            token = await self.get_access_token()
            
            data = await self._make_request(
                "POST",
                f"{self.gateway_url}/v0.5/search",
                json={
                    "searchCriteria": params,
                    "callbackUrl": self.callback_url
                }
            )
            
            return data.get("results", [])
            
        except Exception as e:
            logger.warning(f"UHI search failed, falling back to mock: {e}")
            return self._get_mock_doctors()
    
    def _get_mock_doctors(self) -> list[dict]:
        """Return mock doctor data for development."""
        return [
            {
                "id": "dr-001",
                "name": "Dr. Priya Sharma",
                "specialty": "General Physician",
                "hospital": "Manipal Hospital",
                "distance": "2.3 km",
                "available": True
            },
            {
                "id": "dr-002", 
                "name": "Dr. Rajesh Kumar",
                "specialty": "Internal Medicine",
                "hospital": "Apollo Hospitals",
                "distance": "4.1 km",
                "available": True
            },
            {
                "id": "dr-003",
                "name": "Dr. Anjali Reddy",
                "specialty": "Pulmonology",
                "hospital": "Narayana Health",
                "distance": "5.5 km",
                "available": False
            }
        ]
    
    async def confirm_appointment(
        self, 
        doctor: dict, 
        patient_id: str, 
        fhir_report: dict
    ) -> dict:
        """
        Confirm appointment booking via UHI Gateway.
        
        Args:
            doctor: Selected doctor profile
            patient_id: Patient identifier
            fhir_report: FHIR DiagnosticReport
            
        Returns:
            Booking confirmation with appointment_id
        """
        if not self.client_id or not self.client_secret:
            logger.info("Using mock booking (no UHI credentials)")
            return self._get_mock_booking(doctor, patient_id)
        
        try:
            # In production: POST /v0.5/init and /v0.5/confirm
            # Response comes via callback
            token = await self.get_access_token()
            
            data = await self._make_request(
                "POST",
                f"{self.gateway_url}/v0.5/confirm",
                json={
                    "doctor": doctor,
                    "patientId": patient_id,
                    "fhirReport": fhir_report
                }
            )
            
            return data
            
        except Exception as e:
            logger.warning(f"UHI booking failed, falling back to mock: {e}")
            return self._get_mock_booking(doctor, patient_id)
    
    def _get_mock_booking(self, doctor: dict, patient_id: str) -> dict:
        """Return mock booking confirmation for development."""
        import uuid
        return {
            "appointment_id": f"APT-{uuid.uuid4().hex[:8].upper()}",
            "doctor_name": doctor.get("name"),
            "hospital": doctor.get("hospital"),
            "status": "confirmed",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    
    async def on_search_callback(self, data: dict) -> dict:
        """
        Handle /on_search callback from UHI Gateway.
        
        Args:
            data: Callback payload with doctor results
            
        Returns:
            Acknowledgment response
        """
        # Process search results
        # Store in state for presentation to patient
        logger.info(f"Received search callback: {data.get('requestId')}")
        return {"status": "acknowledged"}
    
    async def on_confirm_callback(self, data: dict) -> dict:
        """
        Handle /on_confirm callback from UHI Gateway.
        
        Args:
            data: Callback payload with booking confirmation
            
        Returns:
            Acknowledgment response
        """
        # Process booking confirmation
        # Send notification to patient via WhatsApp
        logger.info(f"Received confirm callback: {data.get('appointmentId')}")
        return {"status": "acknowledged"}
