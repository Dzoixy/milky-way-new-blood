@router.get("/dashboard")
async def patient_dashboard(request: Request):

    if request.session.get("role") != "Patient":
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "dashboard_patient.html",
        {
            "request": request,
            "risk_percent": None,
            "risk_category": None
        }
    )