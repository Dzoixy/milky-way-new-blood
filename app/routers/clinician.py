from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.database.connection import get_db
from app.models.patient_model import Patient
from app.models.visit_model import Visit
from app.models.risk_result_model import RiskResult

router = APIRouter(prefix="/clinician")
templates = Jinja2Templates(directory="app/templates")


# ==========================
# Context Helper
# ==========================
def clinician_context(request: Request, active: str):
    return {
        "request": request,
        "role": request.session.get("role"),
        "user_name": request.session.get("user_name", "Unknown User"),
        "active": active
    }


# ==========================
# Dashboard
# ==========================
@router.get("/dashboard")
async def clinician_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    result = await db.execute(select(Patient))
    patients = result.scalars().all()

    # ดึง risk ล่าสุดของแต่ละ patient
    for p in patients:
        visit_result = await db.execute(
            select(Visit)
            .where(Visit.patient_id == p.id)
            .order_by(Visit.created_at.desc())
        )
        last_visit = visit_result.scalar_one_or_none()

        if last_visit:
            risk_result = await db.execute(
                select(RiskResult)
                .where(RiskResult.visit_id == last_visit.id)
            )
            risk = risk_result.scalar_one_or_none()
            p.risk_level = risk.risk_level if risk else "-"
        else:
            p.risk_level = "-"

    context = clinician_context(request, "dashboard")
    context["patients"] = patients

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        context
    )


# ==========================
# New Patient Form
# ==========================
@router.get("/new-patient")
async def new_patient_form(request: Request):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    context = clinician_context(request, "new")
    return templates.TemplateResponse("new_patient.html", context)


# ==========================
# Create Patient
# ==========================
@router.post("/new-patient/create")
async def create_patient(
    request: Request,
    full_name: str = Form(...),
    national_id: str = Form(...),
    date_of_birth: date = Form(...),
    gender: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login", status_code=303)

    result = await db.execute(
        select(Patient).where(Patient.national_id == national_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        patient = existing
    else:
        patient = Patient(
            full_name=full_name,
            national_id=national_id,
            date_of_birth=date_of_birth,
            gender=gender,
            user_id=user_id
        )
        db.add(patient)
        await db.commit()
        await db.refresh(patient)

    return RedirectResponse(
        f"/clinician/new-visit/{patient.id}",
        status_code=303
    )


# ==========================
# Visit Form
# ==========================
@router.get("/new-visit/{patient_id}")
async def new_visit_form(
    request: Request,
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        return RedirectResponse("/clinician/dashboard", status_code=303)

    context = clinician_context(request, "new")
    context["patient"] = patient

    return templates.TemplateResponse(
        "new_visit.html",
        context
    )


# ==========================
# Create Visit + Risk
# ==========================
@router.post("/new-visit/{patient_id}")
async def create_visit(
    request: Request,
    patient_id: int,
    sbp: int = Form(...),
    dbp: int = Form(...),
    glucose: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    visit = Visit(
        patient_id=patient_id,
        systolic_bp=sbp,
        diastolic_bp=dbp,
        fasting_glucose=glucose
    )

    db.add(visit)
    await db.commit()
    await db.refresh(visit)

    # Risk Logic
    risk_score = 0
    if sbp > 140:
        risk_score += 1
    if glucose > 126:
        risk_score += 1

    if risk_score == 0:
        level = "LOW"
    elif risk_score == 1:
        level = "MODERATE"
    else:
        level = "HIGH"

    risk = RiskResult(
        visit_id=visit.id,
        risk_level=level,
        risk_score=risk_score
    )

    db.add(risk)
    await db.commit()
    await db.refresh(risk)

    return RedirectResponse(
        f"/clinician/visit/{visit.id}/result",
        status_code=303
    )


# ==========================
# View Result
# ==========================
@router.get("/visit/{visit_id}/result")
async def view_visit_result(
    request: Request,
    visit_id: int,
    db: AsyncSession = Depends(get_db)
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    visit_result = await db.execute(
        select(Visit).where(Visit.id == visit_id)
    )
    visit = visit_result.scalar_one_or_none()

    if not visit:
        return RedirectResponse("/clinician/dashboard", status_code=303)

    risk_result = await db.execute(
        select(RiskResult).where(RiskResult.visit_id == visit.id)
    )
    risk = risk_result.scalar_one_or_none()

    context = clinician_context(request, "dashboard")
    context["visit"] = visit
    context["risk"] = risk

    return templates.TemplateResponse(
        "result_view_clinician.html",
        context
    )