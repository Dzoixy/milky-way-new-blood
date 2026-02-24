def validate_vitals(sbp: int, dbp: int, glucose: int):
    if not (50 <= sbp <= 300):
        raise ValueError("Invalid SBP")

    if not (30 <= dbp <= 200):
        raise ValueError("Invalid DBP")

    if not (40 <= glucose <= 600):
        raise ValueError("Invalid Glucose")