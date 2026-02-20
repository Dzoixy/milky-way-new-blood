from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/patient", tags=["Patient"])
templates = Jinja2Templates(directory="app/templates")


# =========================
# DASHBOARD
# =========================
@router.get("/dashboard", response_class=HTMLResponse)
async def patient_dashboard(request: Request):

    # ตอนนี้ยังไม่มี visit / risk จริง
    risk_percent = None
    risk_category = None

    return templates.TemplateResponse(
        "dashboard_patient.html",
        {
            "request": request,
            "patient_name": "John Doe",
            "risk_percent": risk_percent,
            "risk_category": risk_category
        }
    )


# =========================
# RESULTS PAGE
# =========================
@router.get("/results", response_class=HTMLResponse)
async def patient_results(request: Request):

    visits = []  # ยังไม่มีข้อมูล

    return templates.TemplateResponse(
        "result_view_patient.html",
        {
            "request": request,
            "patient_name": "John Doe",
            "visits": visits
        }
    )