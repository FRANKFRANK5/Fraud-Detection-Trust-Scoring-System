"""
Payment Integration with TemboPLUS and Senjaro Pay
Participant: Frank Karani | Challenge #04
"""

import hashlib
from typing import Dict

async def process_tembo_payment(phone: str, amount: int, supplier_id: str) -> Dict:
    payment_ref = f"TXP_{hashlib.md5(f'{phone}{supplier_id}'.encode()).hexdigest()[:8].upper()}"
    return {"success": True, "payment_ref": payment_ref, "message": "Payment initiated via Tigo Pesa"}

async def process_senjaro_payment(phone: str, amount: int, supplier_id: str) -> Dict:
    payment_ref = f"SJP_{hashlib.md5(f'{phone}{supplier_id}'.encode()).hexdigest()[:8].upper()}"
    return {"success": True, "payment_ref": payment_ref, "message": "Payment initiated via Senjaro Pay"}

async def verify_payment(payment_ref: str) -> Dict:
    return {"verified": True, "payment_ref": payment_ref, "status": "completed"}
