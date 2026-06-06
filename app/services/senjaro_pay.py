"""
TemboPLUS API Integration
Participant: Frank Karani
API: https://tembo.gitbook.io/tembo
"""

import httpx
import hashlib
from typing import Dict

# TemboPLUS Credentials
TEMBO_API_KEY = "7f6ec58ab22b6a294d2c7444"
TEMBO_SECRET = "f24Yj7LqzzCDmrF5Ap19lOWugSIC3zOjRtWfg2oR35h9K+8jbKQkmOMNhGnWV7jp"

async def verify_tembo_payment(phone: str, amount: int, reference: str) -> Dict:
    """
    Verify payment via TemboPLUS API
    """
    url = "https://api.temboplus.co.tz/v1/payment/verify"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "phone": phone,
                "amount": amount,
                "reference": reference,
                "api_key": TEMBO_API_KEY,
                "secret": TEMBO_SECRET
            }
        )
    
    if response.status_code == 200:
        data = response.json()
        return {
            "verified": data.get("status") == "success",
            "transaction_id": data.get("transaction_id"),
            "message": data.get("message", "Payment verified")
        }
    return {"verified": False, "error": "Payment verification failed"}

async def initiate_payment(phone: str, amount: int, description: str) -> Dict:
    """
    Initiate payment via TemboPLUS API
    """
    url = "https://api.temboplus.co.tz/v1/payment/initiate"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "phone": phone,
                "amount": amount,
                "description": description,
                "api_key": TEMBO_API_KEY,
                "secret": TEMBO_SECRET,
                "callback_url": "https://fraud-detection-east-africa.onrender.com/api/v1/payment-callback"
            }
        )
    
    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "payment_ref": data.get("reference"),
            "status": data.get("status"),
            "message": "Payment initiated. Check your Tigo Pesa."
        }
    return {"success": False, "error": "Payment initiation failed"}