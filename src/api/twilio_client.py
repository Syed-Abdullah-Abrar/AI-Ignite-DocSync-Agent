import os
import logging
from twilio.rest import Client
from typing import Optional

logger = logging.getLogger(__name__)

def send_appointment_sms(phone_number: str, patient_name: str, doctor_name: str, appointment_time: str) -> bool:
    """
    Send an SMS confirmation to the patient using Twilio.
    If credentials are not set, it acts as a successful mock.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_PHONE_NUMBER")

    message_body = (
        f"🏥 DocSync UHI: Hello {patient_name}, your appointment with {doctor_name} "
        f"has been CONFIRMED over the ABDM network for {appointment_time}. "
        "Please bring any physical records if applicable."
    )

    if not all([account_sid, auth_token, twilio_number]):
        logger.info(f"[MOCK TWILIO] Would have sent SMS to {phone_number}:\n{message_body}")
        return True

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=phone_number
        )
        logger.info(f"Twilio SMS sent successfully. Message SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Twilio SMS: {str(e)}")
        # In a hackathon demo, we typically don't want the UI to error out just because sms failed
        return False
