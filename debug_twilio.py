import os
import sys
from twilio.rest import Client

def verify_twilio():
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_num = os.environ.get("TWILIO_PHONE_NUMBER")

    if not all([sid, token, from_num]):
        print("❌ ERROR: Twilio Keys are completely missing from your environment vars!")
        return

    print(f"✅ Loaded Twilio SID: {sid[:5]}...")
    print(f"✅ Loaded Twilio FROM: {from_num}")

    target = input("Enter your personal phone number (with country code, e.g., +919876543210): ").strip()
    
    if not target.startswith("+"):
        print("❌ ERROR: Your phone number must start with a '+' and the country code.")
        return

    print("🚀 Sending test message...")
    try:
        client = Client(sid, token)
        msg = client.messages.create(
            body="Hackathon Test — Twilio is working!",
            from_=from_num,
            to=target
        )
        print(f"✅ SUCCESS! SMS Sent. Message SID: {msg.sid}")
    except Exception as e:
        print("\n❌ TWILIO REJECTED THE MESSAGE. Exact reason:")
        print(str(e))

if __name__ == "__main__":
    verify_twilio()
