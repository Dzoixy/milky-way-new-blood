import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import auth, clinician, patient, risk
from app.database.connection import engine, Base

# สร้าง app ก่อนเสมอ
app = FastAPI(title="Milky Way")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router)
app.include_router(clinician.router)
app.include_router(patient.router)
app.include_router(risk.router)


# Startup event (สร้าง table แบบ async)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)