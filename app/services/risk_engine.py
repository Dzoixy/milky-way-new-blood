from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.patient_model import Patient
from app.models.visit_model import Visit

async def calculate_risk_async(
    db: AsyncSession,
    patient_id: int,
    sbp: float,
    dbp: float,
    hba1c: float,
    ldl: float,
    smoking: bool
):
    # ตรวจสอบว่ามี patient จริง
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise ValueError("Patient not found")

    # --- Placeholder scoring logic ---
    risk_score = (
        sbp * 0.05 +
        dbp * 0.03 +
        hba1c * 2.0 +
        ldl * 0.02 +
        (10 if smoking else 0)
    )

    # จัดกลุ่มความเสี่ยง
    if risk_score < 20:
        category = "Low"
    elif risk_score < 40:
        category = "Moderate"
    else:
        category = "High"

    # Feature importance (เรียงจากมากไปน้อย)
    feature_importance = sorted(
        {
            "SBP": sbp * 0.05,
            "DBP": dbp * 0.03,
            "HbA1c": hba1c * 2.0,
            "LDL": ldl * 0.02,
            "Smoking": 10 if smoking else 0
        }.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # บันทึก visit ใหม่
    new_visit = Visit(
        patient_id=patient_id,
        sbp=sbp,
        dbp=dbp,
        risk_score=risk_score
    )

    db.add(new_visit)
    await db.commit()
    await db.refresh(new_visit)

    return {
        "percentage": round(risk_score, 2),
        "category": category,
        "feature_importance": feature_importance
    }