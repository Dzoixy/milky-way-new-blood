from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/clinician", tags=["clinician"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/new-patient")
async def new_patient(request: Request):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse("new_patient.html", {
        "request": request
    })


@router.post("/new-patient")
async def save_patient(
    request: Request,
    full_name: str = Form(...),
    national_id: str = Form(...),
    systolic: float = Form(...),
    diastolic: float = Form(...),
    glucose: float = Form(...),
    cholesterol: float = Form(...),
    age: int = Form(...),
    chronic: str = Form("")
):
    if request.session.get("role") != "clinician":
        return RedirectResponse("/login", status_code=303)

    # ------------------------
    # Risk Calculation (ตัวอย่าง logic)
    # ------------------------
    risk = 0

    if systolic > 140:
        risk += 20
    if glucose > 126:
        risk += 20
    if cholesterol > 240:
        risk += 20
    if age > 60:
        risk += 15
    if "diabetes" in chronic.lower():
        risk += 25

    if risk > 100:
        risk = 100

    # TODO: save patient + visit to DB here

    return RedirectResponse("/clinician/dashboard", status_code=303)