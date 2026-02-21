from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/patient")
templates = Jinja2Templates(directory="app/templates")


def patient_context(request: Request, active: str):
    return {
        "request": request,
        "role": request.session.get("role"),
        "user_name": request.session.get("user_name", "Unknown User"),
        "active": active
    }


# -------------------------
# Patient Dashboard (My Health)
# -------------------------
@router.get("/health")
async def patient_health(request: Request):

    if request.session.get("role") != "patient":
        return RedirectResponse("/login", status_code=303)

    context = patient_context(request, "health")

    return templates.TemplateResponse(
        "dashboard_patient.html",
        context
    )


# -------------------------
# Patient Results
# -------------------------
@router.get("/results")
async def patient_results(request: Request):

    if request.session.get("role") != "patient":
        return RedirectResponse("/login", status_code=303)

    context = patient_context(request, "results")

    return templates.TemplateResponse(
        "patient_results.html",
        context
    )