from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.database.connection import get_db
from app.models.patient_model import Patient
from app.models.visit_model import Visit
from app.models.risk_result_model import RiskResult
from app.services.risk_engine import calculate_risk

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
# Dashboard (Tenant Safe)
# ==========================
@router.get("/dashboard")
async def clinician_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    organization_id = request.session.get("organization_id")

    result = await db.execute(
        select(Patient).where(
            Patient.organization_id == organization_id
        )
    )
    patients = result.scalars().all()

    for p in patients:
        visit_result = await db.execute(
            select(Visit)
            .where(Visit.patient_id == p.id)
            .order_by(desc(Visit.created_at))
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
# Create Patient (Tenant Safe)
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

    organization_id = request.session.get("organization_id")
    user_id = request.session.get("user_id")

    result = await db.execute(
        select(Patient).where(
            Patient.national_id == national_id,
            Patient.organization_id == organization_id
        )
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
            user_id=user_id,
            organization_id=organization_id
        )
        db.add(patient)
        await db.commit()
        await db.refresh(patient)

    return RedirectResponse(
        f"/clinician/new-visit/{patient.id}",
        status_code=303
    )


# ==========================
# Visit Form (Tenant Safe)
# ==========================
@router.get("/new-visit/{patient_id}")
async def new_visit_form(
    request: Request,
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    organization_id = request.session.get("organization_id")

    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.organization_id == organization_id
        )
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
# Create Visit + Risk (Tenant Safe)
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

    organization_id = request.session.get("organization_id")

    # ตรวจสอบว่า patient อยู่ใน tenant นี้จริง
    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.organization_id == organization_id
        )
    )
    patient = result.scalar_one_or_none()

    if not patient:
        return RedirectResponse("/clinician/dashboard", status_code=303)

    visit = Visit(
        patient_id=patient_id,
        systolic_bp=sbp,
        diastolic_bp=dbp,
        fasting_glucose=glucose
    )

    db.add(visit)
    await db.commit()
    await db.refresh(visit)

    level, risk_score = calculate_risk(sbp, glucose)

    risk = RiskResult(
        visit_id=visit.id,
        risk_level=level,
        risk_score=risk_score
    )

    db.add(risk)
    await db.commit()

    return RedirectResponse(
        f"/clinician/visit/{visit.id}/result",
        status_code=303
    )


# ==========================
# View Result (Tenant Safe)
# ==========================
@router.get("/visit/{visit_id}/result")
async def view_visit_result(
    request: Request,
    visit_id: int,
    db: AsyncSession = Depends(get_db)
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    organization_id = request.session.get("organization_id")

    visit_result = await db.execute(
        select(Visit)
        .join(Patient)
        .where(
            Visit.id == visit_id,
            Patient.organization_id == organization_id
        )
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