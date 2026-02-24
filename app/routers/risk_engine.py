def calculate_risk(sbp: int, glucose: int):
    score = 0

    if sbp >= 140:
        score += 1
    if glucose >= 126:
        score += 1

    if score == 0:
        level = "LOW"
    elif score == 1:
        level = "MODERATE"
    else:
        level = "HIGH"

    return level, score