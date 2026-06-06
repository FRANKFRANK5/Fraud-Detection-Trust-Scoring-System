// API URL - Sahihi kwa Render deployment (NEW)
const API_URL = "https://fraud-detection-trust-scoring-system.onrender.com";

// LED Functions
function updateRiskLED(riskLevel) {
    const led = document.getElementById('riskLed');
    if (!led) return;
    led.className = 'risk-led';
    switch(riskLevel) {
        case 'HIGH': led.classList.add('high'); break;
        case 'MEDIUM': led.classList.add('medium'); break;
        case 'LOW': led.classList.add('low'); break;
        default: led.classList.add('off');
    }
}

function resetRiskLED() {
    const led = document.getElementById('riskLed');
    if (led) led.className = 'risk-led off';
}

function startLEDIdleBlink() {
    const led = document.getElementById('riskLed');
    if (led) {
        led.className = 'risk-led off';
    }
}

// FUNCTION KUU: Inasasisha matokeo yote kwa pamoja (Kushoto na Kulia)
async function updateBothSides(fraudScore, trustScore, riskLevel, reasons) {
    
    // 1. TENGENEZA VIGEZO VYA MAAMUZI
    let rightRiskLevel = "";
    let recommendation = "";
    
    if (trustScore >= 70) {
        rightRiskLevel = "LOW";
        recommendation = "APPROVE";
    } else if (trustScore >= 50) {
        rightRiskLevel = "MEDIUM";
        recommendation = "REVIEW";
    } else {
        rightRiskLevel = "HIGH";
        recommendation = "REJECT";
    }

    // 2. SASISHA KUSHOTO (Result Card)
    const riskClass = rightRiskLevel.toLowerCase();
    document.getElementById("result").className = `result show ${riskClass}`;
    
    let fraudStatus = fraudScore >= 60 ? "🚨 FRAUD DETECTED!" : 
                     fraudScore >= 30 ? "⚠️ POTENTIAL FRAUD DETECTED" : "✅ No Fraud Detected";
    let fraudColor = fraudScore >= 60 ? "#dc2626" : fraudScore >= 30 ? "#f59e0b" : "#22c55e";
    
    document.getElementById("result").innerHTML = `
        <div style="font-weight: bold; margin-bottom: 8px; color: ${fraudColor};">${fraudStatus}</div>
        <div class="fraud-score">Fraud Score: ${fraudScore}%</div>
        <div>Trust Score: ${trustScore}%</div>
        <div>Risk Level: <strong>${rightRiskLevel}</strong></div>
        ${reasons.length ? `<div style="margin-top: 12px;"><strong>Reasons:</strong></div>
        <ul class="reasons">${reasons.map(r => `<li>${r}</li>`).join('')}</ul>` : 
        '<div style="margin-top: 12px;">✅ No suspicious patterns detected</div>'}
    `;
    
    // 3. SASISHA KULIA (Trust Score Check Card)
    const bgColor = rightRiskLevel === "HIGH" ? "#fee2e2" : rightRiskLevel === "MEDIUM" ? "#fff3e0" : "#dcfce7";
    const textColor = rightRiskLevel === "HIGH" ? "#dc2626" : rightRiskLevel === "MEDIUM" ? "#f59e0b" : "#064e3b";
    
    document.getElementById("trustResult").innerHTML = `
        <div style="background: ${bgColor}; padding: 15px; border-radius: 12px;">
            <div style="font-size: 28px; font-weight: bold; color: ${textColor};">${trustScore}%</div>
            <div style="font-size: 13px; margin-top: 5px;"><strong>Risk Level:</strong> ${rightRiskLevel}</div>
            <div style="font-size: 13px;"><strong>Recommendation:</strong> ${recommendation}</div>
            <div style="font-size: 11px; margin-top: 8px; color: #666;">Based on Fraud Score: ${fraudScore}%</div>
        </div>
    `;
    
    // 4. SASISHA TAA YA LED
    updateRiskLED(rightRiskLevel);
}

async function detectFraudAndUpdateAll(data) {
    const response = await fetch(`${API_URL}/api/v1/detect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

// CHECK TRUST SCORE - INAPATA DATA KUTOKA KWA FORM
async function checkTrustScore() {
    const userId = document.getElementById("trustUserId").value;
    const listingId = document.getElementById("listingId").value;
    const title = document.getElementById("title").value;
    const price = parseFloat(document.getElementById("price").value);
    const location = document.getElementById("location").value;
    const city = document.getElementById("city").value;
    const bedrooms = parseInt(document.getElementById("bedrooms").value);
    const description = document.getElementById("description").value;
    const has_images = document.getElementById("hasImages").value === "true";
    const user_account_days = parseInt(document.getElementById("userAge").value);
    const user_verified = document.getElementById("userVerified").value === "true";
    
    const data = {
        listing_id: listingId,
        title: title,
        price: price,
        location: location,
        city: city,
        bedrooms: bedrooms,
        description: description,
        has_images: has_images,
        user_id: userId,
        user_account_days: user_account_days,
        user_verified: user_verified
    };
    
    try {
        const result = await detectFraudAndUpdateAll(data);
        const trustScore = 100 - result.fraud_score;
        await updateBothSides(result.fraud_score, trustScore, result.risk_level, result.reasons);
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("trustResult").innerHTML = `
            <div style="color: red; padding: 15px;">
                Error: Could not calculate trust score. ${error.message}
            </div>
        `;
    }
}

async function loadScenarios() {
    try {
        const response = await fetch(`${API_URL}/api/v1/scenarios`);
        const scenarios = await response.json();
        const html = scenarios.map(s => `
            <div class="scenario-item">
                <h4>⚠️ ${s.name}</h4>
                <p>${s.description}</p>
                <div class="indicators">
                    ${s.indicators.map(i => `<span class="indicator">${i}</span>`).join('')}
                </div>
            </div>
        `).join('');
        document.getElementById("scenariosList").innerHTML = html;
    } catch (error) {
        console.error("Error loading scenarios:", error);
        document.getElementById("scenariosList").innerHTML = `
            <div style="color: red; padding: 20px; text-align: center;">
                Error loading scenarios. Please refresh the page.
            </div>
        `;
    }
}

// DETECT FRAUD BUTTON
document.getElementById("fraudForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    resetRiskLED();
    
    const resultDiv = document.getElementById("result");
    resultDiv.className = "result show";
    resultDiv.innerHTML = '<div style="text-align: center; padding: 20px;">🔄 Analyzing listing...</div>';
    
    const data = {
        listing_id: document.getElementById("listingId").value,
        title: document.getElementById("title").value,
        price: parseFloat(document.getElementById("price").value),
        location: document.getElementById("location").value,
        city: document.getElementById("city").value,
        bedrooms: parseInt(document.getElementById("bedrooms").value),
        description: document.getElementById("description").value,
        has_images: document.getElementById("hasImages").value === "true",
        user_id: document.getElementById("userId").value,
        user_account_days: parseInt(document.getElementById("userAge").value),
        user_verified: document.getElementById("userVerified").value === "true"
    };
    
    try {
        const result = await detectFraudAndUpdateAll(data);
        const trustScore = 100 - result.fraud_score;
        await updateBothSides(result.fraud_score, trustScore, result.risk_level, result.reasons);
    } catch (error) {
        console.error("ERROR:", error);
        document.getElementById("result").innerHTML = `<div style="color: red; padding: 20px;">Error: ${error.message}</div>`;
    }
});

// Hakikisha trustUserId inalingana na userId kwenye form
document.getElementById("userId").addEventListener("input", function() {
    document.getElementById("trustUserId").value = this.value;
});

startLEDIdleBlink();
loadScenarios();

console.log("Script loaded successfully. API_URL:", API_URL);
