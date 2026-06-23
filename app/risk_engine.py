def calculate_risk(files_changed):

    score = 0
    reasons = []

    for file in files_changed:

        file = file.lower()

        if "database" in file:
            score += 40
            reasons.append("Database file changed")

        if "auth" in file:
            score += 30
            reasons.append("Authentication module changed")

        if "docker" in file:
            score += 20
            reasons.append("Docker configuration changed")

        if "jenkins" in file:
            score += 20
            reasons.append("CI/CD pipeline changed")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level, reasons