import asyncio


async def calculate_risk_async(sbp: float, dbp: float):

    await asyncio.sleep(0)

    # ---------------------------
    # Simple Risk Logic (Demo)
    # ---------------------------

    risk_percent = 0

    # SBP scoring
    if sbp >= 180:
        risk_percent += 40
    elif sbp >= 160:
        risk_percent += 30
    elif sbp >= 140:
        risk_percent += 20
    elif sbp >= 130:
        risk_percent += 10

    # DBP scoring
    if dbp >= 110:
        risk_percent += 30
    elif dbp >= 100:
        risk_percent += 20
    elif dbp >= 90:
        risk_percent += 10

    # Cap at 95%
    risk_percent = min(risk_percent, 95.0)

    # ---------------------------
    # Category
    # ---------------------------
    if risk_percent < 10:
        category = "Low"
    elif risk_percent < 20:
        category = "Mild"
    elif risk_percent < 35:
        category = "Moderate"
    elif risk_percent < 60:
        category = "High"
    else:
        category = "Very High"

    # ---------------------------
    # Ranked Factors (Demo)
    # ---------------------------
    ranked_factors = []

    if sbp >= 140:
        ranked_factors.append({"factor": "Systolic BP", "impact": "High"})

    if dbp >= 90:
        ranked_factors.append({"factor": "Diastolic BP", "impact": "Moderate"})

    if not ranked_factors:
        ranked_factors.append({"factor": "Blood Pressure", "impact": "Stable"})

    # ---------------------------
    # Return Standard Structure
    # ---------------------------
    return {
        "risk_percent": float(risk_percent),
        "category": category,
        "ranked_factors": ranked_factors,
        "recommendation": "Lifestyle modification and monitoring"
    }