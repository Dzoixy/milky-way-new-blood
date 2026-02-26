from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from datetime import datetime

from app.database.connection import AsyncSessionLocal
from app.models.patient_model import Patient
from app.models.visit_model import Visit

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
        "organization_id": request.session.get("organization_id"),
        "role": request.session.get("role"),  # สำคัญมาก
    }


def require_clinician(request: Request):
    if request.session.get("role") != "clinician":
        raise HTTPException(status_code=403, detail="Unauthorized")

    if not request.session.get("organization_id"):
        raise HTTPException(status_code=400, detail="Invalid session")


# ======================================================
# DASHBOARD
# ======================================================

@router.get("/dashboard")
async def clinician_dashboard(request: Request):

    require_clinician(request)
    org_id = request.session.get("organization_id")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Patient).where(Patient.organization_id == org_id)
        )
        patients = result.scalars().all()

    context = clinician_context(request, "dashboard")
    context["patients"] = patients

    return templates.TemplateResponse("dashboard_clinician.html", context)


# ======================================================
# NEW PATIENT (MULTI STEP)
# ======================================================

@router.get("/new-patient")
async def new_patient_form(request: Request):

    require_clinician(request)

    step = request.query_params.get("step", "a")
    patient_id = request.query_params.get("patient_id")

    patient = None

    if patient_id:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Patient).where(
                    Patient.id == int(patient_id),
                    Patient.organization_id == request.session.get("organization_id")
                )
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

    require_clinician(request)

    user_id = request.session.get("user_id")
    org_id = request.session.get("organization_id")

    dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()

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

    require_clinician(request)
    org_id = request.session.get("organization_id")

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Patient).where(
                Patient.id == patient_id,
                Patient.organization_id == org_id
            )
        )
        patient = result.scalar_one_or_none()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        visit = Visit(
            patient_id=patient_id,
            organization_id=org_id,
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

    require_clinician(request)
    org_id = request.session.get("organization_id")

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Visit).where(
                Visit.id == visit_id,
                Visit.organization_id == org_id
            )
        )
        visit = result.scalar_one_or_none()

        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        visit.smoking = smoking
        visit.alcohol = alcohol

        await db.commit()

    return RedirectResponse(
        f"/clinician/new-patient?step=d&patient_id={patient_id}&visit_id={visit_id}",
        status_code=303
    )


# ======================================================
# STEP D — SAVE MEDICAL + CALCULATE RISK
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

    require_clinician(request)
    org_id = request.session.get("organization_id")

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Visit).where(
                Visit.id == visit_id,
                Visit.organization_id == org_id
            )
        )
        visit = result.scalar_one_or_none()

        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        visit.chronic_diseases = chronic
        visit.family_history = family
        visit.allergies = allergies
        visit.notes = notes

        # Risk logic
        risk_score = 0

        if visit.systolic_bp and visit.systolic_bp >= 140:
            risk_score += 1
        if visit.fasting_glucose and visit.fasting_glucose >= 126:
            risk_score += 1
        if visit.bmi and visit.bmi >= 30:
            risk_score += 1

        if risk_score == 0:
            visit.risk_level = "LOW"
        elif risk_score == 1:
            visit.risk_level = "MODERATE"
        else:
            visit.risk_level = "HIGH"

        visit.risk_score = risk_score

        await db.commit()

    return RedirectResponse(
        f"/clinician/result/{visit_id}",
        status_code=303
    )


# ======================================================
# RESULT PAGE
# ======================================================

@router.get("/result/{visit_id}")
async def view_result(request: Request, visit_id: int):

    require_clinician(request)
    org_id = request.session.get("organization_id")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Visit).where(
                Visit.id == visit_id,
                Visit.organization_id == org_id
            )
        )
        visit = result.scalar_one_or_none()

    if not visit:
        return RedirectResponse("/clinician/dashboard", status_code=303)

    context = clinician_context(request, "results")  # สำคัญมาก
    context["visit"] = visit

    return templates.TemplateResponse(
        "result_view_clinician.html",
        context
    )