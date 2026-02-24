from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.database.connection import AsyncSessionLocal
from app.models.patient_model import Patient

router = APIRouter(prefix="/clinician")
templates = Jinja2Templates(directory="app/templates")


# ==============================
# Helper Context
# ==============================

def clinician_context(request: Request, active: str):
    return {
        "request": request,
        "active_tab": active,
        "user_name": request.session.get("user_name"),
        "organization_id": request.session.get("organization_id")
    }


# ==============================
# NEW PATIENT FORM (GET)
# ==============================

@router.get("/new-patient")
async def new_patient_form(request: Request):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    # รับ step จาก query param
    step = request.query_params.get("step", "a")

    context = clinician_context(request, "new")
    context["step"] = step

    return templates.TemplateResponse("new_patient.html", context)


# ==============================
# CREATE PATIENT (POST)
# ==============================

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

    async with AsyncSessionLocal() as db:

        new_patient = Patient(
            full_name=full_name,
            national_id=national_id,
            date_of_birth=date_of_birth,
            gender=gender,
            organization_id=request.session.get("organization_id")
        )

        db.add(new_patient)
        await db.commit()
        await db.refresh(new_patient)

    # ไป step D ต่อ
    return RedirectResponse(
        f"/clinician/new-patient?step=d",
        status_code=303
    )