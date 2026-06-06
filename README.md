<<<<<<< HEAD
# 🛡️ Fraud Detection & Trust Scoring System

## East African Rental Market | Hackathon Challenge #04

**Participant:** Frank Karani | **Country:** Tanzania

---

### 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run API
python app/main.py

# Open browser
http://localhost:8000
http://localhost:8000/docs

📡 API Endpoints
Method	Endpoint	Description
POST	/api/v1/detect	Detect fraud in rental listing
GET	/api/v1/trust-score/{user_id}	Get user trust score (0-100)
GET	/api/v1/scenarios	List all 6 detection scenarios
🎯 Detection Scenarios
#	Scenario	Description
1	Phantom Listing	Property doesn't physically exist
2	Price Anomaly	Unrealistic pricing vs market
3	Rapid Listing	Mass listing posting pattern
4	Identity Theft	Fake or stolen user identity
5	Payment Fraud	Deposit and payment scams
6	Image Fraud	Stock or stolen property photos
📊 Fraud Detection Factors
Factor	Weight	Description
Price Anomaly	35%	Comparison with EA market data
User Behavior	25%	Account age, verification status
Content Analysis	20%	Keywords, images, description
Geographic	10%	City and location validation
Metadata	10%	Listing ID and price patterns
✅ Deliverables Complete

    Fraud detection model

    Risk scoring system (0-100 trust score)

    6 detection scenarios

🧪 Test Examples

Legitimate Listing (Low Risk):

    Price: $550 for 2BR in Dar es Salaam

    Account: 365 days old, verified

    Has images, good description

Fraudulent Listing (High Risk):

    Price: $150 for 3BR in Dar es Salaam (60% below market)

    Account: 1 day old, unverified

    No images, urgent deposit request

🔄 Methodology Transfer: Credit Card Fraud → Rental Fraud
Kaggle Feature	Mapped to Rental Feature	Weight
Amount	Price anomaly vs market average	35%
Time	User account age & behavior	25%
V1-V28 (PCA)	Content analysis (keywords, images)	20%
V3 (PCA pattern)	Geographic validation	10%
V5 (PCA pattern)	Listing metadata	10%

Why This Transfer Works:

    Credit card fraud uses transaction amount anomalies → Rental fraud uses price anomalies

    Credit card fraud uses time patterns → Rental fraud uses user account age

    Credit card fraud uses PCA components → Rental fraud uses content quality indicators

🏆 Judging Criteria
Criteria	Weight	Implementation
Security Depth	30%	6 detection scenarios, LED monitor, input validation
Technical Implementation	25%	FastAPI, Pydantic, async, clean code
Business Relevance	25%	East African market focus (TZ, KE, UG)
Innovation	20%	LIVE RISK MONITOR, traffic light LED, 6 scenarios
🌍 East African Market Coverage
Country	Cities Supported
Tanzania	Dar es Salaam, Arusha, Mwanza, Zanzibar, Dodoma
Kenya	Nairobi, Mombasa, Kisumu, Nakuru, Eldoret
Uganda	Kampala, Entebbe, Jinja, Gulu, Mbarara
🛡️ Cold-Start Prevention Strategy

The system uses Heuristic Rules combined with real-time analysis:

    New accounts (<7 days) trigger +18 fraud score

    Unverified users trigger +15 fraud score

    No images trigger +12 fraud score

This prevents scammers from posting fake listings before they can build trust history.
🔮 Future Integration

The system is designed to integrate with East African digital identity systems:

    NIDA e-KYC (Tanzania) - User verification

    NaPA Digital Addressing - Location validation

    Huduma Namba (Kenya) - Identity verification

    NIN (Uganda) - National ID validation

=======
# Fraud-Detection-Trust-Scoring-System
Real-time fraud detection and trust scoring system for East African rental market with SMS and payment integration. Built for Pumzika Hackathon 2026.
>>>>>>> 862582c8acf731f7a6c07f212812a08cf2ce9a69
