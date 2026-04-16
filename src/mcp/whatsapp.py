"""
WhatsApp MCP Integration

Model Context Protocol server for WhatsApp messaging.
"""
import httpx
from typing import Optional
from src.config import config


class WhatsAppMCP:
    """WhatsApp message handler via MCP."""
    
    def __init__(self):
        self.api_key = config.messaging.api_key
        self.base_url = "https://api.whatsapp.com/v1"
    
    async def send_message(self, phone: str, message: str) -> dict:
        """
        Send WhatsApp message to patient.
        
        Args:
            phone: Patient phone number
            message: Message content
            
        Returns:
            Send confirmation dict
        """
        if not self.api_key:
            # Mock response for development
            return {
                "status": "mock",
                "to": phone,
                "message": message
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "to": phone,
                    "type": "text",
                    "text": {"body": message}
                }
            )
            return response.json()
    
    async def send_template(self, phone: str, template: str, params: dict) -> dict:
        """
        Send WhatsApp template message.
        
        Args:
            phone: Patient phone number
            template: Template name
            params: Template parameters
            
        Returns:
            Send confirmation dict
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "to": phone,
                    "type": "template",
                    "template": {
                        "name": template,
                        "language": {"code": "en"},
                        "components": params
                    }
                }
            )
            return response.json()
    
    def format_appointment_confirmation(
        self,
        doctor_name: str,
        hospital: str,
        time: str,
        appointment_id: str
    ) -> str:
        """Format appointment confirmation message."""
        return f"""✅ Appointment Confirmed

👨‍⚕️ {doctor_name}
🏥 {hospital}
🕐 {time}

📋 Appointment ID: {appointment_id}

Please arrive 15 minutes early with your ID.

- DocSync Healthcare"""
    
    def format_emergency_message(self, instructions: str) -> str:
        """Format emergency instructions message."""
        return f"""🚨 MEDICAL EMERGENCY

{instructions}

If you believe this is a life-threatening emergency, call 108 immediately.

- DocSync Healthcare"""
