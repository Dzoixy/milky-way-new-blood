from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
):

    request.session["role"] = role

    if role == "Clinician":
        return RedirectResponse("/clinician/dashboard", status_code=303)

    if role == "Patient":
        return RedirectResponse("/patient/dashboard", status_code=303)

    return RedirectResponse("/login", status_code=303)