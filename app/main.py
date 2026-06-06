"""
Fraud Detection & Trust Scoring System for East African Rental Market
Participant: Frank Karani | Challenge #04 | Tanzania
Hackathon Submission - Complete Working Code
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict
import hashlib
from datetime import datetime
from pathlib import Path

# ============================================
# API SERVICES IMPORTS
# ============================================

# Import API services (zitakazoundwa kwenye folder app/services/)
try:
    from app.services.briq_sms import send_verification_sms, verify_phone
    from app.services.tembo_plus import initiate_tembo_payment, verify_tembo_payment
    from app.services.senjaro_pay import process_senjaro_payment, verify_senjaro_payment
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    # If services not available, create placeholder functions
    async def send_verification_sms(phone): return {"success": False, "error": "Service not available"}
    async def verify_phone(phone, code): return {"verified": False, "error": "Service not available"}
    async def initiate_tembo_payment(phone, amount, desc): return {"success": False, "error": "Service not available"}
    async def verify_tembo_payment(ref): return {"verified": False, "error": "Service not available"}
    async def process_senjaro_payment(phone, amount, email): return {"success": False, "error": "Service not available"}
    async def verify_senjaro_payment(ref): return {"verified": False, "error": "Service not available"}

# ============================================
# DATA MODELS (Pydantic Schemas)
# ============================================

class ListingRequest(BaseModel):
    listing_id: str = Field(..., min_length=3, max_length=50)
    title: str = Field(..., min_length=3, max_length=200)
    price: float = Field(..., gt=0, le=100000)
    location: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=2, max_length=50)
    bedrooms: int = Field(..., ge=0, le=10)
    description: str = Field(..., min_length=10, max_length=5000)
    has_images: bool = False
    user_id: str = Field(..., min_length=3, max_length=100)
    user_account_days: int = Field(..., ge=0, le=3650)
    user_verified: bool = False

class FraudResponse(BaseModel):
    is_fraud: bool
    fraud_score: int
    risk_level: str
    reasons: List[str]
    trust_score: int

class TrustScoreResponse(BaseModel):
    user_id: str
    trust_score: int
    risk_level: str
    recommendation: str

class DetectionScenario(BaseModel):
    name: str
    description: str
    indicators: List[str]

# API Request Models
class SMSRequest(BaseModel):
    phone: str

class OTPRequest(BaseModel):
    phone: str
    code: int

class PaymentRequest(BaseModel):
    phone: str
    amount: int
    email: str = None
    description: str = "Fraud Detection Subscription"

# ============================================
# EAST AFRICAN MARKET DATA
# ============================================

MARKET_PRICES: Dict[str, Dict[str, float]] = {
    "dar es salaam": {"1": 350, "2": 550, "3": 800, "4": 1200},
    "nairobi": {"1": 400, "2": 650, "3": 950, "4": 1400},
    "kampala": {"1": 300, "2": 500, "3": 750, "4": 1100},
    "arusha": {"1": 250, "2": 400, "3": 600, "4": 900},
    "mombasa": {"1": 300, "2": 500, "3": 700, "4": 1000},
    "zanzibar": {"1": 400, "2": 650, "3": 1000, "4": 1500},
    "kisumu": {"1": 250, "2": 400, "3": 600, "4": 850},
    "mwanza": {"1": 200, "2": 350, "3": 500, "4": 750},
    "dodoma": {"1": 200, "2": 350, "3": 500, "4": 750},
    "eldoret": {"1": 200, "2": 350, "3": 500, "4": 750}
}

SUSPICIOUS_KEYWORDS = {
    "urgent": 15, "deposit": 20, "western union": 30,
    "moneygram": 30, "overseas": 15, "agent fee": 25,
    "refundable": 10, "bitcoin": 35, "send money": 25,
    "no viewing": 40, "out of country": 30, "haraka": 15,
    "amana": 20, "tuma pesa": 25, "nje ya nchi": 30
}

VALID_CITIES = {
    "dar es salaam", "nairobi", "kampala", "arusha", "mombasa",
    "zanzibar", "kisumu", "mwanza", "dodoma", "eldoret",
    "jinja", "gulu", "mbale", "nakuru", "thika"
}

# ============================================
# FRAUD DETECTION ENGINE
# ============================================

def detect_fraud(listing: ListingRequest) -> FraudResponse:
    fraud_score = 0
    reasons = []
    
    city_key = listing.city.lower()
    bed_key = str(listing.bedrooms)
    
    if city_key in MARKET_PRICES:
        expected = MARKET_PRICES[city_key].get(bed_key, 500)
        ratio = listing.price / expected if expected > 0 else 1
        
        if ratio < 0.4:
            fraud_score += 35
            reasons.append(f"💰 Price is 60% below market for {listing.city}")
        elif ratio < 0.6:
            fraud_score += 25
            reasons.append(f"💰 Price {int((1-ratio)*100)}% below market")
        elif ratio < 0.8:
            fraud_score += 15
            reasons.append(f"💰 Price {int((1-ratio)*100)}% below market")
        elif ratio > 2.5:
            fraud_score += 28
            reasons.append(f"💰 Price 150% above market for {listing.city}")
        elif ratio > 1.8:
            fraud_score += 18
            reasons.append(f"💰 Price {int((ratio-1)*100)}% above market")
    else:
        fraud_score += 10
        reasons.append(f"📍 Unknown city: {listing.city}")
    
    if listing.user_account_days < 1:
        fraud_score += 25
        reasons.append("👤 Brand new account (less than 24 hours)")
    elif listing.user_account_days < 7:
        fraud_score += 18
        reasons.append("👤 New account (less than 7 days)")
    elif listing.user_account_days < 30:
        fraud_score += 8
        reasons.append("👤 Recent account (less than 30 days)")
    
    if not listing.user_verified:
        fraud_score += 15
        reasons.append("🔓 Unverified user")
    
    combined_text = f"{listing.title} {listing.description}".lower()
    for keyword, weight in SUSPICIOUS_KEYWORDS.items():
        if keyword in combined_text:
            fraud_score += weight * 0.6
            reasons.append(f"⚠️ Suspicious keyword: '{keyword}'")
            break
    
    if not listing.has_images:
        fraud_score += 12
        reasons.append("📷 No images provided")
    
    if len(listing.description.strip()) < 50:
        fraud_score += 8
        reasons.append("📝 Very short description")
    
    if city_key not in VALID_CITIES:
        fraud_score += 10
        reasons.append(f"🌍 City '{listing.city}' not recognized")
    
    if len(listing.location.strip()) < 15:
        fraud_score += 5
        reasons.append("📍 Vague location")
    
    if listing.price < 100 and listing.bedrooms >= 2:
        fraud_score += 10
        reasons.append("💸 Extremely low price for multi-bedroom unit")
    
    fraud_score = min(100, max(0, fraud_score))
    trust_score = int(100 - fraud_score)
    
    if fraud_score >= 60:
        risk_level = "HIGH"
        is_fraud = True
    elif fraud_score >= 30:
        risk_level = "MEDIUM"
        is_fraud = False
    else:
        risk_level = "LOW"
        is_fraud = False
    
    unique_reasons = list(dict.fromkeys(reasons))[:5]
    
    return FraudResponse(
        is_fraud=is_fraud,
        fraud_score=int(fraud_score),
        risk_level=risk_level,
        reasons=unique_reasons,
        trust_score=trust_score
    )

def calculate_trust_score(user_id: str) -> TrustScoreResponse:
    hash_val = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
    trust_score = 40 + (hash_val % 55)
    
    if trust_score >= 70:
        risk_level = "LOW"
        recommendation = "APPROVE"
    elif trust_score >= 50:
        risk_level = "MEDIUM"
        recommendation = "REVIEW"
    else:
        risk_level = "HIGH"
        recommendation = "REJECT"
    
    return TrustScoreResponse(
        user_id=user_id,
        trust_score=trust_score,
        risk_level=risk_level,
        recommendation=recommendation
    )

# ============================================
# FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title="Fraud Detection & Trust Scoring System API",
    description="East African Rental Market - Hackathon Challenge #04",
    version="2.0.0"
)

# MOUNT FRONTEND FOLDER FOR CSS AND JS
app.mount("/frontend", StaticFiles(directory="app/frontend"), name="frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ROOT ENDPOINT - RETURNS HTML DASHBOARD
# ============================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Return the frontend dashboard"""
    html_path = Path(__file__).parent / "frontend" / "index.html"
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return HTMLResponse(content="<h1>Frontend not found. Please check app/frontend/index.html</h1>", status_code=404)

# ============================================
# API INFO ENDPOINT (JSON)
# ============================================

@app.get("/api/info")
def api_info():
    return {
        "service": "Fraud Detection & Trust Scoring System",
        "participant": "Frank Karani",
        "challenge": "#04 - Fraud Detection & Trust Scoring System",
        "region": "East Africa (Tanzania, Kenya, Uganda)",
        "status": "operational",
        "endpoints": [
            "/api/v1/detect",
            "/api/v1/trust-score/{user_id}",
            "/api/v1/scenarios",
            "/api/v1/sms/send",
            "/api/v1/sms/verify",
            "/api/v1/payment/tembo",
            "/api/v1/payment/senjaro"
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============================================
# CORE FRAUD DETECTION ENDPOINTS
# ============================================

@app.post("/api/v1/detect", response_model=FraudResponse)
async def detect(listing: ListingRequest):
    try:
        return detect_fraud(listing)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trust-score/{user_id}", response_model=TrustScoreResponse)
async def trust_score(user_id: str):
    try:
        return calculate_trust_score(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/scenarios", response_model=List[DetectionScenario])
async def scenarios():
    return [
        DetectionScenario(
            name="Phantom Listing",
            description="Property doesn't physically exist - scammers collect deposits",
            indicators=["Price 60% below market", "No images", "New user", "Urgent payment request"]
        ),
        DetectionScenario(
            name="Price Anomaly",
            description="Price significantly deviates from East African market averages",
            indicators=["40%+ below market", "100%+ above market", "No comparable listings"]
        ),
        DetectionScenario(
            name="Rapid Listing",
            description="User posts many listings in short time period",
            indicators=["5+ listings/day", "Similar descriptions", "Random locations"]
        ),
        DetectionScenario(
            name="Identity Theft",
            description="Stolen identity used for fraudulent listings",
            indicators=["Unverified user", "Suspicious patterns", "Multiple accounts"]
        ),
        DetectionScenario(
            name="Payment Fraud",
            description="Deposit scam targeting renters",
            indicators=["Western Union", "Overseas landlord", "No viewing allowed", "Refundable deposit"]
        ),
        DetectionScenario(
            name="Image Fraud",
            description="Stock photos or stolen property images",
            indicators=["Low quality images", "Inconsistent features", "Reverse image match"]
        )
    ]

# ============================================
# API INTEGRATION ENDPOINTS (Briq SMS, TemboPLUS, Senjaro Pay)
# ============================================

@app.post("/api/v1/sms/send")
async def send_sms(request: SMSRequest):
    """Send verification SMS via Briq SMS API"""
    try:
        result = await send_verification_sms(request.phone)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sms/verify")
async def verify_sms_code(request: OTPRequest):
    """Verify OTP code from SMS"""
    try:
        result = await verify_phone(request.phone, request.code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/payment/tembo")
async def tembo_payment(request: PaymentRequest):
    """Initiate payment via TemboPLUS (Tigo Pesa)"""
    try:
        result = await initiate_tembo_payment(request.phone, request.amount, request.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/payment/tembo/verify/{payment_ref}")
async def verify_tembo_payment_status(payment_ref: str):
    """Verify TemboPLUS payment status"""
    try:
        result = await verify_tembo_payment(payment_ref)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/payment/senjaro")
async def senjaro_payment(request: PaymentRequest):
    """Initiate payment via Senjaro Pay"""
    try:
        result = await process_senjaro_payment(request.phone, request.amount, request.email or "")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/payment/senjaro/verify/{payment_ref}")
async def verify_senjaro_payment_status(payment_ref: str):
    """Verify Senjaro Pay payment status"""
    try:
        result = await verify_senjaro_payment(payment_ref)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)