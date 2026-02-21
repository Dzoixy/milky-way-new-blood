from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.connection import get_db
from app.models.patient_model import Patient
from app.models.visit_model import Visit
from app.models.risk_result_model import RiskResult
from app.services.risk_engine import calculate_risk_async

router = APIRouter(prefix="/risk")


# ======================================
# Calculate Risk (Clinician only)
# ======================================
@router.post("/calculate")
async def calculate_risk(
    request: Request,
    patient_id: int = Form(...),
    sbp: float = Form(...),
    dbp: float = Form(...),
    db: AsyncSession = Depends(get_db)
):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    # ตรวจว่ามี patient จริง
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        return RedirectResponse("/clinician/dashboard", status_code=303)

    # 🔹 คำนวณ risk
    risk_data = await calculate_risk_async(sbp=sbp, dbp=dbp)

    # 🔹 สร้าง Visit
    new_visit = Visit(
        patient_id=patient.id,
        sbp=sbp,
        dbp=dbp,
        risk_score=risk_data["risk_percent"]
    )

    db.add(new_visit)
    await db.commit()
    await db.refresh(new_visit)

    # 🔹 สร้าง RiskResult
    new_risk = RiskResult(
        visit_id=new_visit.id,
        risk_percent=risk_data["risk_percent"],
        category=risk_data["category"],
        full_json=risk_data
    )

    db.add(new_risk)
    await db.commit()

    # redirect ไปหน้า result ของ visit
    return RedirectResponse(
        f"/clinician/visit/{new_visit.id}/result",
        status_code=303
    )