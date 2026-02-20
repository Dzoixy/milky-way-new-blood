from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/clinician", tags=["Clinician"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def clinician_dashboard(request: Request):

    if request.session.get("role") != "Clinician":
        return RedirectResponse("/login", status_code=303)

    patients = []

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        {
            "request": request,
            "patients": patients
        }
    )