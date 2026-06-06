"""
Senjaro Pay API Integration
Participant: Frank Karani
API: https://senjaropay-473150.docs.buildwithfern.com
"""

import httpx
from typing import Dict

# Senjaro Pay Credentials
SENJARO_SECRET = "senj_live_sk_CBrTFrU0mWdshUsErzDH68qlYLt2tPWB7A_e"
SENJARO_PUBLIC = "senj_live_pk_laTYVdUIIJ9GManmTVttWicydI2k9g1oGyIk"

async def process_senjaro_payment(phone: str, amount: int, email: str) -> Dict:
    """
    Process payment via Senjaro Pay API
    """
    url = "https://api.senjaropay.com/v1/payment/create"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "amount": amount,
                "currency": "TZS",
                "phone": phone,
                "email": email,
                "description": "Fraud Detection System Subscription",
                "callback_url": "https://fraud-detection-east-africa.onrender.com/api/v1/payment-webhook"
            },
            headers={
                "Authorization": f"Bearer {SENJARO_SECRET}",
                "X-Public-Key": SENJARO_PUBLIC
            }
        )
    
    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "payment_url": data.get("payment_url"),
            "reference": data.get("reference"),
            "message": "Payment link generated"
        }
    return {"success": False, "error": "Payment processing failed"}

async def verify_senjaro_payment(reference: str) -> Dict:
    """
    Verify payment status
    """
    url = f"https://api.senjaropay.com/v1/payment/status/{reference}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {SENJARO_SECRET}"}
        )
    
    if response.status_code == 200:
        data = response.json()
        return {
            "verified": data.get("status") == "completed",
            "amount": data.get("amount"),
            "message": data.get("message", "Payment verified")
        }
    return {"verified": False, "error": "Verification failed"}