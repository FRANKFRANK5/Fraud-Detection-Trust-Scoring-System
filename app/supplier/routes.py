"""
Supplier Routes for Registration and Dashboard
Participant: Frank Karani | Challenge #04
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.subscription.models import SupplierManager, SUBSCRIPTION_PLANS
from app.subscription.payment import process_tembo_payment, process_senjaro_payment, verify_payment

router = APIRouter(prefix="/supplier", tags=["Supplier"])
supplier_manager = SupplierManager()

class RegisterRequest(BaseModel):
    business_name: str
    email: str
    phone: str
    location: str
    plan: str
    payment_method: str

@router.post("/register")
async def register_supplier(data: RegisterRequest):
    supplier = supplier_manager.register(data.dict())
    plan_price = SUBSCRIPTION_PLANS.get(data.plan, {}).get("price_tzs", 50000)
    
    if data.payment_method == "tembo":
        payment = await process_tembo_payment(data.phone, plan_price, supplier["supplier_id"])
    else:
        payment = await process_senjaro_payment(data.phone, plan_price, supplier["supplier_id"])
    
    return {
        "supplier_id": supplier["supplier_id"],
        "api_key": supplier["api_key"],
        "payment_ref": payment["payment_ref"],
        "message": "Registration successful. Complete payment to activate."
    }

@router.get("/activate")
async def activate_subscription(supplier_id: str, payment_ref: str, plan: str):
    payment_status = await verify_payment(payment_ref)
    if not payment_status["verified"]:
        raise HTTPException(status_code=400, detail="Payment not verified")
    
    result = supplier_manager.activate_subscription(supplier_id, plan, payment_ref)
    return result

@router.get("/dashboard/{supplier_id}")
async def get_dashboard(supplier_id: str, api_key: str):
    verification = supplier_manager.verify_api_key(api_key)
    if not verification["valid"]:
        raise HTTPException(status_code=401, detail=verification["reason"])
    
    return {
        "supplier_id": supplier_id,
        "business_name": "Your Business",
        "api_key": api_key,
        "api_endpoint": "https://fraud-detection-east-africa.onrender.com/api/v1/detect",
        "documentation": "https://fraud-detection-east-africa.onrender.com/docs",
        "stats": {
            "requests_used": 150,
            "requests_limit": 500,
            "frauds_detected": 12
        }
    }
