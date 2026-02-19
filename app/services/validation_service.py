def validate_vital_signs(
    sbp: float,
    dbp: float,
    hba1c: float,
    ldl: float
):
    errors = []

    if sbp < 50 or sbp > 300:
        errors.append("Invalid SBP range")

    if dbp < 30 or dbp > 200:
        errors.append("Invalid DBP range")

    if hba1c < 3 or hba1c > 20:
        errors.append("Invalid HbA1c range")

    if ldl < 0 or ldl > 500:
        errors.append("Invalid LDL range")

    return errors