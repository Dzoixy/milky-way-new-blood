from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/clinician")
templates = Jinja2Templates(directory="app/templates")


def clinician_context(request: Request, active: str):
    return {
        "request": request,
        "role": request.session.get("role"),
        "user_name": request.session.get("user_name", "Unknown User"),
        "active": active
    }


# -------------------------
# Dashboard
# -------------------------
@router.get("/dashboard")
async def clinician_dashboard(request: Request):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    context = clinician_context(request, "dashboard")
    context["patients"] = []

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        context
    )


# -------------------------
# New Patient (GET)
# -------------------------
@router.get("/new-patient")
async def new_patient_form(request: Request):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    context = clinician_context(request, "new")

    return templates.TemplateResponse(
        "new_patient.html",
        context
    )


# -------------------------
# New Patient (POST)
# -------------------------
@router.post("/new-patient")
async def create_patient(
    request: Request,
    full_name: str = Form(...),
    national_id: str = Form(...)
):

    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    # save DB here

    return RedirectResponse("/clinician/dashboard", status_code=303)