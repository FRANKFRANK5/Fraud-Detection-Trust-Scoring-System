"""
Supplier and Subscription Models
Participant: Frank Karani | Challenge #04
"""

from datetime import datetime, timedelta
import secrets
from typing import Dict

# Subscription plans
SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "Basic",
        "price_tzs": 50000,
        "duration_days": 30,
        "requests_limit": 500,
        "features": ["fraud_detection", "trust_score"]
    },
    "premium": {
        "name": "Premium",
        "price_tzs": 100000,
        "duration_days": 30,
        "requests_limit": 2000,
        "features": ["fraud_detection", "trust_score", "url_scanner", "api_access"]
    },
    "enterprise": {
        "name": "Enterprise",
        "price_tzs": 250000,
        "duration_days": 90,
        "requests_limit": 10000,
        "features": ["all_features", "webhook", "analytics", "priority_support"]
    }
}

class SupplierManager:
    def __init__(self):
        self.suppliers = {}
    
    def register(self, data: Dict) -> Dict:
        supplier_id = f"SUP_{secrets.token_hex(4).upper()}"
        api_key = f"FK_{secrets.token_urlsafe(32)}"
        
        supplier = {
            "supplier_id": supplier_id,
            "business_name": data.get("business_name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "location": data.get("location"),
            "api_key": api_key,
            "registered_at": datetime.now().isoformat(),
            "subscription": None,
            "status": "pending"
        }
        self.suppliers[supplier_id] = supplier
        return supplier
    
    def activate_subscription(self, supplier_id: str, plan_name: str, payment_ref: str) -> Dict:
        plan = SUBSCRIPTION_PLANS.get(plan_name)
        if not plan:
            return {"error": "Invalid plan"}
        
        supplier = self.suppliers.get(supplier_id)
        if not supplier:
            return {"error": "Supplier not found"}
        
        expires_at = datetime.now() + timedelta(days=plan["duration_days"])
        
        supplier["subscription"] = {
            "plan": plan_name,
            "price": plan["price_tzs"],
            "start_date": datetime.now().isoformat(),
            "expiry_date": expires_at.isoformat(),
            "requests_used": 0,
            "requests_limit": plan["requests_limit"],
            "features": plan["features"],
            "payment_ref": payment_ref
        }
        supplier["status"] = "active"
        
        return {
            "supplier_id": supplier_id,
            "api_key": supplier["api_key"],
            "expiry_date": expires_at.isoformat(),
            "features": plan["features"]
        }
    
    def verify_api_key(self, api_key: str) -> Dict:
        for sid, supplier in self.suppliers.items():
            if supplier.get("api_key") == api_key:
                sub = supplier.get("subscription")
                if not sub:
                    return {"valid": False, "reason": "No active subscription"}
                
                expiry = datetime.fromisoformat(sub["expiry_date"])
                if expiry < datetime.now():
                    return {"valid": False, "reason": "Subscription expired"}
                
                if sub["requests_used"] >= sub["requests_limit"]:
                    return {"valid": False, "reason": "Request limit exceeded"}
                
                sub["requests_used"] += 1
                
                return {
                    "valid": True,
                    "supplier_id": sid,
                    "supplier_name": supplier["business_name"],
                    "features": sub["features"]
                }
        return {"valid": False, "reason": "Invalid API key"}
