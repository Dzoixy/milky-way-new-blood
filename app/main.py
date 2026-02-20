import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth, clinician, patient, risk
from app.database.connection import engine, Base

app = FastAPI(title="Milky Way")

# -------------------------
# -------------------------
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-change-this"
)

# -------------------------
# Static
# -------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# -------------------------
# Templates
# -------------------------
templates = Jinja2Templates(directory="app/templates")

# -------------------------
# Routers
# -------------------------
app.include_router(auth.router)
app.include_router(clinician.router)
app.include_router(patient.router)
app.include_router(risk.router)

# -------------------------
# Startup
# -------------------------
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)