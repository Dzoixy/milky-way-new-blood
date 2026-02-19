from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.risk_engine import calculate_risk_async
router = APIRouter(prefix="/risk")
templates = Jinja2Templates(directory="app/templates")

@router.post("/calculate", response_class=HTMLResponse)
async def calculate(request: Request, sbp: float = Form(...)):
    risk_result = await calculate_risk_async(sbp)
    return templates.TemplateResponse(
        "result_view_clinician.html",
        {"request": request, "risk": risk_result}
    )