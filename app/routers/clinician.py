from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from datetime import datetime

from app.database.connection import AsyncSessionLocal
from app.models.patient_model import Patient
from app.models.visit_model import Visit   # ต้องมี model นี้

router = APIRouter(prefix="/clinician")
templates = Jinja2Templates(directory="app/templates")


# ======================================================
# Helper
# ======================================================

def clinician_context(request: Request, active: str):
    return {
        "request": request,
        "active_tab": active,
        "user_name": request.session.get("user_name"),
        "organization_id": request.session.get("organization_id")
    }


# ======================================================
# DASHBOARD
# ======================================================

@router.get("/dashboard")
async def clinician_dashboard(request: Request):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    org_id = request.session.get("organization_id")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Patient).where(Patient.organization_id == org_id)
        )
        patients = result.scalars().all()

    context = clinician_context(request, "dashboard")
    context["patients"] = patients

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        context
    )


# ======================================================
# NEW PATIENT (MULTI STEP)
# ======================================================

@router.get("/new-patient")
async def new_patient_form(request: Request):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    step = request.query_params.get("step", "a")
    patient_id = request.query_params.get("patient_id")

    patient = None

    if patient_id:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Patient).where(Patient.id == int(patient_id))
            )
            patient = result.scalar_one_or_none()

    context = clinician_context(request, "new")
    context["step"] = step
    context["patient"] = patient

    return templates.TemplateResponse("new_patient.html", context)


# ======================================================
# STEP A — CREATE PATIENT
# ======================================================

@router.post("/new-patient/create")
async def create_patient(
    request: Request,
    full_name: str = Form(...),
    national_id: str = Form(...),
    date_of_birth: str = Form(...),
    gender: str = Form(...)
):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    user_id = request.session.get("user_id")
    org_id = request.session.get("organization_id")

    if not user_id or not org_id:
        raise HTTPException(status_code=400, detail="Session invalid")

    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    async with AsyncSessionLocal() as db:

        new_patient = Patient(
            full_name=full_name.strip(),
            national_id=national_id.strip(),
            date_of_birth=dob,
            gender=gender,
            user_id=user_id,
            organization_id=org_id
        )

        db.add(new_patient)
        await db.commit()
        await db.refresh(new_patient)

    return RedirectResponse(
        f"/clinician/new-patient?step=b&patient_id={new_patient.id}",
        status_code=303
    )


# ======================================================
# STEP B — SAVE VITAL SIGNS
# ======================================================

@router.post("/save-vitals")
async def save_vitals(
    request: Request,
    patient_id: int = Form(...),
    systolic_bp: int = Form(...),
    diastolic_bp: int = Form(...),
    fasting_glucose: float = Form(...),
    bmi: float = Form(...)
):

    async with AsyncSessionLocal() as db:

        visit = Visit(
            patient_id=patient_id,
            systolic_bp=systolic_bp,
            diastolic_bp=diastolic_bp,
            fasting_glucose=fasting_glucose,
            bmi=bmi
        )

        db.add(visit)
        await db.commit()
        await db.refresh(visit)

    return RedirectResponse(
        f"/clinician/new-patient?step=c&patient_id={patient_id}&visit_id={visit.id}",
        status_code=303
    )


# ======================================================
# STEP C — SAVE LIFESTYLE
# ======================================================

@router.post("/save-lifestyle")
async def save_lifestyle(
    request: Request,
    patient_id: int = Form(...),
    visit_id: int = Form(...),
    smoking: str = Form(...),
    alcohol: str = Form(...)
):

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Visit).where(Visit.id == visit_id)
        )
        visit = result.scalar_one()

        visit.smoking = smoking
        visit.alcohol = alcohol

        await db.commit()

    return RedirectResponse(
        f"/clinician/new-patient?step=d&patient_id={patient_id}&visit_id={visit_id}",
        status_code=303
    )


# ======================================================
# STEP D — SAVE MEDICAL HISTORY + FINISH
# ======================================================

@router.post("/save-medical")
async def save_medical(
    request: Request,
    patient_id: int = Form(...),
    visit_id: int = Form(...),
    chronic: str = Form(""),
    family: str = Form(""),
    allergies: str = Form(""),
    notes: str = Form("")
):

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Visit).where(Visit.id == visit_id)
        )
        visit = result.scalar_one()

        visit.chronic_diseases = chronic
        visit.family_history = family
        visit.allergies = allergies
        visit.notes = notes

        # ====== ตรงนี้ใส่ Risk Engine ได้ ======
        # visit.risk_score = calculate_risk(...)
        # visit.risk_level = "HIGH"

        await db.commit()

    return RedirectResponse(
        "/clinician/dashboard",
        status_code=303
    )
