import asyncio

async def calculate_risk_async(sbp: float):
    await asyncio.sleep(0)
    return {
        "percentage": 12.5,
        "category": "Moderate",
        "top_factors": ["SBP", "LDL", "Smoking"]
    }