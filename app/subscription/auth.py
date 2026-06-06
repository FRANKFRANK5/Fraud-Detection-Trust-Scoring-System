"""
API Key Authentication Middleware
Participant: Frank Karani | Challenge #04
"""

from fastapi import HTTPException, Request
from app.subscription.models import SupplierManager

supplier_manager = SupplierManager()

async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    verification = supplier_manager.verify_api_key(api_key)
    if not verification["valid"]:
        raise HTTPException(status_code=401, detail=verification["reason"])
    
    return verification
