from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.patient_model import Patient
from app.models.visit_model import Visit
from app.models.risk_result_model import RiskResult

router = APIRouter(prefix="/patient")
templates = Jinja2Templates(directory="app/templates")


# ==========================
# Context Helper
# ==========================
def patient_context(request: Request, active: str):
    return {
        "request": request,
        "role": request.session.get("role"),
        "user_name": request.session.get("user_name", "Unknown User"),
        "active": active
    }


# ==========================
# Dashboard (My Health)
# ==========================
@router.get("/dashboard")
async def patient_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    if request.session.get("role") != "patient":
        return RedirectResponse("/login", status_code=303)

    username = request.session.get("user_name")

    # username = national_id
    result = await db.execute(
        select(Patient).where(Patient.national_id == username)
    )
    patient = result.scalar_one_or_none()

    latest_visit = None
    latest_risk = None

    if patient:
        visit_result = await db.execute(
            select(Visit)
            .where(Visit.patient_id == patient.id)
            .order_by(Visit.created_at.desc())
        )
        latest_visit = visit_result.scalars().first()

        if latest_visit:
            risk_result = await db.execute(
                select(RiskResult)
                .where(RiskResult.visit_id == latest_visit.id)
            )
            latest_risk = risk_result.scalar_one_or_none()

    context = patient_context(request, "health")
    context["patient"] = patient
    context["visit"] = latest_visit
    context["risk"] = latest_risk

    return templates.TemplateResponse(
        "dashboard_patient.html",
        context
    )


# ==========================
# Results Page
# ==========================
@router.get("/results")
async def patient_results(
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    if request.session.get("role") != "patient":
        return RedirectResponse("/login", status_code=303)

    username = request.session.get("user_name")

    result = await db.execute(
        select(Patient).where(Patient.national_id == username)
    )
    patient = result.scalar_one_or_none()

    latest_visit = None
    latest_risk = None

    if patient:
        visit_result = await db.execute(
            select(Visit)
            .where(Visit.patient_id == patient.id)
            .order_by(Visit.created_at.desc())
        )
        latest_visit = visit_result.scalars().first()

        if latest_visit:
            risk_result = await db.execute(
                select(RiskResult)
                .where(RiskResult.visit_id == latest_visit.id)
            )
            latest_risk = risk_result.scalar_one_or_none()

    context = patient_context(request, "results")
    context["patient"] = patient
    context["visit"] = latest_visit
    context["risk"] = latest_risk

    return templates.TemplateResponse(
        "patient_results.html",
        context
    )