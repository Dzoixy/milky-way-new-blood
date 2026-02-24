import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, clinician
from app.database.connection import engine, Base


# ======================================================
# App Init
# ======================================================

app = FastAPI(
    title="Milky Way Clinical DSS",
    version="1.0.0"
)


# ======================================================
# Session Middleware
# ======================================================

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "dev-secret-key"),
    same_site="lax",
    https_only=False   # Render ใช้ https อยู่แล้ว
)


# ======================================================
# Static Files
# ======================================================

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# ======================================================
# Routers
# ======================================================

app.include_router(auth.router)
app.include_router(clinician.router)


# ======================================================
# Database Startup
# ======================================================

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ======================================================
# Root Redirect
# ======================================================

@app.get("/")
async def root():
    return RedirectResponse("/login", status_code=303)