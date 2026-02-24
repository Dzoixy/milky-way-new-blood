import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, clinician, patient
from app.database.connection import engine, Base

# =========================================
# App Init
# =========================================

app = FastAPI(
    title="Milky Way Clinical DSS",
    version="1.0.0"
)

# =========================================
# Session Middleware (Production-safe)
# =========================================

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-this-in-production"),
    same_site="lax",
    https_only=True
)

# =========================================
# Static Files
# =========================================

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# =========================================
# Routers
# =========================================

app.include_router(auth.router)
app.include_router(clinician.router)
app.include_router(patient.router)
# =========================================
# Database Startup
# =========================================

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# =========================================
# Root Redirect
# =========================================

@app.get("/")
async def root():
    return RedirectResponse("/login", status_code=303)