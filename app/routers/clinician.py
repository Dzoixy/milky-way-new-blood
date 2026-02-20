@router.get("/dashboard")
async def clinician_dashboard(request: Request):

    if request.session.get("role") != "Clinician":
        return RedirectResponse("/login", status_code=303)

    patients = []

    return templates.TemplateResponse(
        "dashboard_clinician.html",
        {
            "request": request,
            "patients": patients
        }
    )