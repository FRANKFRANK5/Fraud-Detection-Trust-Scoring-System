"""
Briq SMS API Integration
Participant: Frank Karani
API: https://docs.briq.tz
"""

import httpx
from typing import Dict

# Briq API Credentials
BRIQ_API_KEY = "BRIQ-9D03-J6B9"  # Your invite code

async def send_verification_sms(phone: str) -> Dict:
    """
    Send OTP via Briq SMS API
    """
    # Generate 6-digit OTP
    import random
    otp = random.randint(100000, 999999)
    
    # Briq API endpoint
    url = "https://api.briq.tz/v1/sms/send"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "to": phone,
                "message": f"Your Fraud Detection verification code: {otp}",
                "api_key": BRIQ_API_KEY
            }
        )
    
    if response.status_code == 200:
        return {"success": True, "otp": otp, "message": "SMS sent successfully"}
    else:
        return {"success": False, "error": "Failed to send SMS"}

async def verify_phone(phone: str, code: int) -> Dict:
    """
    Verify phone number with OTP
    """
    # In production, store OTP in database
    # For demo, we'll accept any 6-digit code
    if 100000 <= code <= 999999:
        return {"verified": True, "message": "Phone verified successfully"}
    return {"verified": False, "message": "Invalid code"}