from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.user_model import User
from app.models.organization_model import Organization
from app.utils.security import verify_password, hash_password

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
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        return RedirectResponse("/login", status_code=303)

    if not verify_password(password, user.password_hash):
        return RedirectResponse("/login", status_code=303)

    # Store session (Multi-tenant critical)
    request.session["user_id"] = user.id
    request.session["role"] = user.role
    request.session["user_name"] = user.username
    request.session["organization_id"] = user.organization_id

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

@router.get("/seed-admin")
async def seed_admin(db: AsyncSession = Depends(get_db)):

    # Create organization if not exists
    org_result = await db.execute(select(Organization))
    org = org_result.scalar_one_or_none()

    if not org:
        org = Organization(name="Default Clinic")
        db.add(org)
        await db.commit()
        await db.refresh(org)

    # Check admin exists
    result = await db.execute(
        select(User).where(User.username == "admin")
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {"message": "Admin already exists"}

    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),
        role="clinician",
        organization_id=org.id
    )

    db.add(admin)
    await db.commit()
