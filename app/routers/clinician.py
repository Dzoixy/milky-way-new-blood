from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/clinician", tags=["Clinician"])
templates = Jinja2Templates(directory="app/templates")


# =========================
# Dashboard
# =========================
@router.get("/dashboard")
async def clinician_dashboard(request: Request):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    # ตัวอย่าง mock data
    patients = []

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        {
            "request": request,
            "patients": patients
        }
    )


# =========================
# Add New Patient (GET)
# =========================
@router.get("/new-patient")
async def new_patient_form(request: Request):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "new_patient.html",
        {"request": request}
    )


# =========================
# Add New Patient (POST)
# =========================
@router.post("/new-patient")
async def create_patient(
    request: Request,
    full_name: str = Form(...),
    national_id: str = Form(...)
):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    # TODO: บันทึก DB ตรงนี้

    return RedirectResponse("/clinician/dashboard", status_code=303)


# =========================
# View Patient
# =========================
@router.get("/patient/{patient_id}")
async def view_patient(request: Request, patient_id: int):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    # TODO: ดึงข้อมูล patient จาก DB

    return templates.TemplateResponse(
        "patient_detail.html",
        {
            "request": request,
            "patient_id": patient_id
        }
    )


# =========================
# New Visit
# =========================
@router.get("/patient/{patient_id}/new-visit")
async def new_visit(request: Request, patient_id: int):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "new_visit.html",
        {
            "request": request,
            "patient_id": patient_id
        }
    )