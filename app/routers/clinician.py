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

    context = clinician_context(request, "dashboard")
    context["patients"] = patients

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        context
    )


# ==========================
# View Patient Detail
# ==========================
@router.get("/patient/{patient_id}")
async def view_patient(
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

    visit_result = await db.execute(
        select(Visit)
        .where(Visit.patient_id == patient.id)
        .order_by(Visit.created_at.desc())
    )
    visits = visit_result.scalars().all()

    context = clinician_context(request, "dashboard")
    context["patient"] = patient
    context["visits"] = visits

    return templates.TemplateResponse(
        "patient_detail_clinician.html",
        context
    )


# ==========================
# View Visit Result
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


# ==========================
# New Patient (GET)
# ==========================
@router.get("/new-patient")
async def new_patient_form(request: Request):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    context = clinician_context(request, "new")

    return templates.TemplateResponse(
        "new_patient.html",
        context
    )


# ==========================
# New Patient (POST)
# ==========================
@router.post("/new-patient")
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

    result = await db.execute(
        select(Patient).where(Patient.national_id == national_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return RedirectResponse("/clinician/new-patient", status_code=303)

    new_patient = Patient(
        full_name=full_name,
        national_id=national_id,
        date_of_birth=date_of_birth,
        gender=gender
    )

    db.add(new_patient)
    await db.commit()

    return RedirectResponse("/clinician/dashboard", status_code=303)