from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.database.connection import AsyncSessionLocal
from app.models.user_model import User
from app.utils.security import verify_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# =========================================
# Login Page
# =========================================

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


# =========================================
# Login Process
# =========================================

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

    if not user:
        return RedirectResponse("/login", status_code=303)

    if not verify_password(password, user.password_hash):
        return RedirectResponse("/login", status_code=303)

    # 🔥 Multi-Tenant Critical
    request.session["user_id"] = user.id
    request.session["role"] = user.role
    request.session["user_name"] = user.username
    request.session["organization_id"] = user.organization_id   # ✅ สำคัญมาก

    # Redirect by role
    if user.role == "clinician":
        return RedirectResponse("/clinician/dashboard", status_code=303)

    if user.role == "patient":
        return RedirectResponse("/patient/dashboard", status_code=303)

    return RedirectResponse("/login", status_code=303)


# =========================================
# Logout
# =========================================

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)