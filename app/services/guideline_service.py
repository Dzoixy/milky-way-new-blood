async def generate_guideline_async(risk_category: str):
    if risk_category == "Low":
        return {
            "medication": "Lifestyle modification only",
            "monitoring": "Annual check-up",
            "contraindications": []
        }

    if risk_category == "Moderate":
        return {
            "medication": "Consider statin",
            "monitoring": "6-month follow-up",
            "contraindications": ["Check liver function"]
        }

    if risk_category == "High":
        return {
            "medication": "Statin + BP control",
            "monitoring": "3-month follow-up",
            "contraindications": ["Monitor kidney function"]
        }

    return {}