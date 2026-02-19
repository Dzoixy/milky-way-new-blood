from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

router = APIRouter(prefix="/clinician")
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def clinician_dashboard(request: Request):

    patients = []   # ตอนนี้ยังไม่มีข้อมูลผู้ใช้

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        {
            "request": request,
            "patients": patients,
            "current_date": datetime.now().strftime("%A, %d %B %Y")
        }
    )