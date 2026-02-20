from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/clinician", tags=["Clinician"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def clinician_dashboard(request: Request):

    patients = []  # ยังไม่มีข้อมูลจริง

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        {
            "request": request,
            "patients": patients
        }
    )